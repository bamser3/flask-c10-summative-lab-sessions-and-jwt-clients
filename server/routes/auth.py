from flask import Blueprint, request, jsonify
from models import db, User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(
        username=data['username'],
        password_hash=hashed_pw
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Invalid password"}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
                "token": token,
                    "user": {
                        "id": user.id,
                        "username": user.username
                    }
                }), 200

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(
        username=data['username'],
        password_hash=hashed_pw
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201
