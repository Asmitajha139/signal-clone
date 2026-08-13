from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.contact import ContactCreate, ContactResponse
from app.models.contact import Contact
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/contacts", tags=["contacts"])

@router.get("", response_model=List[ContactResponse])
def get_contacts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contacts = db.query(Contact).filter(Contact.user_id == current_user.id).all()
    return contacts

@router.post("", response_model=ContactResponse)
def add_contact(data: ContactCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target_user = db.query(User).filter(
        (User.username == data.contact_username_or_phone) | (User.phone_number == data.contact_username_or_phone)
    ).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="Contact user not found")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a contact")

    existing = db.query(Contact).filter(
        Contact.user_id == current_user.id,
        Contact.contact_user_id == target_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User is already in your contacts")

    new_contact = Contact(user_id=current_user.id, contact_user_id=target_user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@router.delete("/{contact_id}")
def delete_contact(contact_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"message": "Contact removed successfully"}
