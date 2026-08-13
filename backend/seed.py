import sys
import datetime
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import User, Contact, Conversation, ConversationMember, Message, MessageRead
from app.utils.security import hash_password

def seed_database():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Clear existing data
        db.query(MessageRead).delete()
        db.query(Message).delete()
        db.query(ConversationMember).delete()
        db.query(Conversation).delete()
        db.query(Contact).delete()
        db.query(User).delete()
        db.commit()

        print("Seeding Users...")
        users_data = [
            {
                "username": "alex",
                "phone_number": "+12345678901",
                "password_hash": hash_password("password123"),
                "display_name": "Alex Mercer",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=Alex",
                "status": "🔒 Signal privacy enthusiast. Building secure apps.",
                "is_online": True
            },
            {
                "username": "priya",
                "phone_number": "+12345678902",
                "password_hash": hash_password("password123"),
                "display_name": "Priya Sharma",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=Priya",
                "status": "Available for real-time secure messaging.",
                "is_online": True
            },
            {
                "username": "rahul",
                "phone_number": "+12345678903",
                "password_hash": hash_password("password123"),
                "display_name": "Rahul Verma",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=Rahul",
                "status": "Working on WebSockets & FastAPI.",
                "is_online": False
            },
            {
                "username": "neha",
                "phone_number": "+12345678904",
                "password_hash": hash_password("password123"),
                "display_name": "Neha Gupta",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=Neha",
                "status": "UI/UX Designer | Signal Aesthetics",
                "is_online": True
            },
            {
                "username": "john",
                "phone_number": "+12345678905",
                "password_hash": hash_password("password123"),
                "display_name": "John Doe",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=John",
                "status": "Testing & QA Lead",
                "is_online": False
            }
        ]

        users = {}
        for udata in users_data:
            user = User(**udata)
            db.add(user)
            db.flush()
            users[user.username] = user

        print("Seeding Contacts...")
        # Add contacts for Alex
        for target in ["priya", "rahul", "neha", "john"]:
            db.add(Contact(user_id=users["alex"].id, contact_user_id=users[target].id))
            db.add(Contact(user_id=users[target].id, contact_user_id=users["alex"].id))

        # Priya's contacts
        db.add(Contact(user_id=users["priya"].id, contact_user_id=users["rahul"].id))
        db.add(Contact(user_id=users["rahul"].id, contact_user_id=users["priya"].id))

        db.commit()

        print("Seeding Direct Conversations...")
        now = datetime.datetime.utcnow()

        # Direct 1: Alex & Priya
        c1 = Conversation(type="direct", created_at=now - datetime.timedelta(days=2), updated_at=now - datetime.timedelta(minutes=5))
        db.add(c1)
        db.flush()
        db.add(ConversationMember(conversation_id=c1.id, user_id=users["alex"].id, role="member"))
        db.add(ConversationMember(conversation_id=c1.id, user_id=users["priya"].id, role="member"))

        m1_1 = Message(
            conversation_id=c1.id,
            sender_id=users["alex"].id,
            content="Hey Priya! Welcome to the new Signal platform.",
            status="read",
            created_at=now - datetime.timedelta(hours=2)
        )
        m1_2 = Message(
            conversation_id=c1.id,
            sender_id=users["priya"].id,
            content="Hey Alex! The UI looks amazing. Are WebSockets enabled?",
            status="read",
            created_at=now - datetime.timedelta(hours=1, minutes=45)
        )
        m1_3 = Message(
            conversation_id=c1.id,
            sender_id=users["alex"].id,
            content="Yes! Real-time messaging, typing indicators, delivery and read receipts are all functional.",
            status="read",
            created_at=now - datetime.timedelta(minutes=15)
        )
        m1_4 = Message(
            conversation_id=c1.id,
            sender_id=users["priya"].id,
            content="Awesome! See you in the group chat.",
            status="read",
            created_at=now - datetime.timedelta(minutes=5)
        )
        db.add_all([m1_1, m1_2, m1_3, m1_4])

        # Direct 2: Alex & Rahul
        c2 = Conversation(type="direct", created_at=now - datetime.timedelta(days=1), updated_at=now - datetime.timedelta(hours=3))
        db.add(c2)
        db.flush()
        db.add(ConversationMember(conversation_id=c2.id, user_id=users["alex"].id, role="member"))
        db.add(ConversationMember(conversation_id=c2.id, user_id=users["rahul"].id, role="member"))

        m2_1 = Message(
            conversation_id=c2.id,
            sender_id=users["rahul"].id,
            content="Hey Alex, did you check the SQLite schema?",
            status="read",
            created_at=now - datetime.timedelta(hours=4)
        )
        m2_2 = Message(
            conversation_id=c2.id,
            sender_id=users["alex"].id,
            content="Yes, SQLAlchemy relationships and normalized models look super clean.",
            status="delivered",
            created_at=now - datetime.timedelta(hours=3)
        )
        db.add_all([m2_1, m2_2])

        # Direct 3: Alex & Neha
        c3 = Conversation(type="direct", created_at=now - datetime.timedelta(hours=5), updated_at=now - datetime.timedelta(hours=1))
        db.add(c3)
        db.flush()
        db.add(ConversationMember(conversation_id=c3.id, user_id=users["alex"].id, role="member"))
        db.add(ConversationMember(conversation_id=c3.id, user_id=users["neha"].id, role="member"))

        m3_1 = Message(
            conversation_id=c3.id,
            sender_id=users["neha"].id,
            content="Hi Alex! I reviewed the dark theme colors and rounded message bubbles.",
            status="sent",
            created_at=now - datetime.timedelta(hours=1)
        )
        db.add(m3_1)

        print("Seeding Group Conversation...")
        # Group 1: Signal Engineering Team
        cg = Conversation(type="group", name="Signal Engineering Team", created_at=now - datetime.timedelta(days=3), updated_at=now - datetime.timedelta(minutes=2))
        db.add(cg)
        db.flush()

        db.add(ConversationMember(conversation_id=cg.id, user_id=users["alex"].id, role="admin"))
        db.add(ConversationMember(conversation_id=cg.id, user_id=users["priya"].id, role="member"))
        db.add(ConversationMember(conversation_id=cg.id, user_id=users["rahul"].id, role="member"))
        db.add(ConversationMember(conversation_id=cg.id, user_id=users["neha"].id, role="member"))

        mg_sys = Message(
            conversation_id=cg.id,
            sender_id=users["alex"].id,
            content="Alex Mercer created the group 'Signal Engineering Team'",
            message_type="system",
            status="read",
            created_at=now - datetime.timedelta(days=3)
        )
        mg_1 = Message(
            conversation_id=cg.id,
            sender_id=users["alex"].id,
            content="Welcome everyone! Let's build the best 24-hour SDE messaging platform.",
            status="read",
            created_at=now - datetime.timedelta(hours=5)
        )
        mg_2 = Message(
            conversation_id=cg.id,
            sender_id=users["priya"].id,
            content="Frontend is built with Next.js & Tailwind CSS!",
            status="read",
            created_at=now - datetime.timedelta(hours=4)
        )
        mg_3 = Message(
            conversation_id=cg.id,
            sender_id=users["rahul"].id,
            content="Backend REST APIs & WebSockets are running smoothly on FastAPI.",
            status="read",
            created_at=now - datetime.timedelta(hours=2)
        )
        mg_4 = Message(
            conversation_id=cg.id,
            sender_id=users["neha"].id,
            content="Great work team! Group chats, admin permissions, and real-time syncing are ready.",
            status="read",
            created_at=now - datetime.timedelta(minutes=2)
        )

        db.add_all([mg_sys, mg_1, mg_2, mg_3, mg_4])

        db.commit()
        print("Database seeded successfully with fake users, contacts, conversations, and messages!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
