from flask_bcrypt import Bcrypt
from app import app
from models import db, User, Note

bcrypt = Bcrypt(app)

with app.app_context():
    db.drop_all()
    db.create_all()

    hashed_pw = bcrypt.generate_password_hash("1234").decode('utf-8')

    user1 = User(username="testuser", password_hash=hashed_pw)
    user2 = User(username="user2", password_hash=hashed_pw)

    db.session.add_all([user1, user2])
    db.session.commit()

    note1 = Note(title="Note 1", content="Hello", user_id=user1.id)
    note2 = Note(title="Note 2", content="World", user_id=user1.id)

    db.session.add_all([note1, note2])
    db.session.commit()

    print("Seeded.")