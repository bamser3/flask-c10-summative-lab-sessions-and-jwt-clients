from flask import Flask, request, jsonify
from models import db, Note, User
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from routes.auth import auth_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key'
app.config["JWT_SECRET_KEY"] = "super-secret-key"

jwt = JWTManager(app)

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return {"message": "API is running!"}

@app.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    return jsonify({
        "id": user.id,
        "username": user.username
    }), 200

@app.route('/notes', methods=['POST'])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    note = Note(
        title=data['title'],
        content=data['content'],
        user_id=user_id
    )

    db.session.add(note)
    db.session.commit()

    return jsonify({"message": "Created"}), 201


@app.route('/notes', methods=['GET'])
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    notes = Note.query.filter_by(user_id=user_id)\
        .paginate(page=page, per_page=per_page)

    return jsonify({
        "data": [
            {"id": n.id, "title": n.title, "content": n.content}
            for n in notes.items
        ],
        "total": notes.total
    })


@app.route('/notes/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_note(id):
    user_id = int(get_jwt_identity())

    note = Note.query.filter_by(id=id, user_id=user_id).first()

    if not note:
        return {"error": "Not found"}, 404

    db.session.delete(note)
    db.session.commit()

    return {"message": "Deleted"}

@app.route('/notes/<int:id>', methods=['PATCH'])
@jwt_required()
def update_note(id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    note = Note.query.filter_by(id=id, user_id=user_id).first()

    if not note:
        return {"error": "Not found"}, 404

    if "title" in data:
        note.title = data["title"]

    if "content" in data:
        note.content = data["content"]

    db.session.commit()

    return jsonify({
        "id": note.id,
        "title": note.title,
        "content": note.content
    }), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)