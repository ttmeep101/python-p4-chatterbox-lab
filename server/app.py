from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=["GET", "POST"])
def messages():
    if request.method == 'GET':
        messages = db.session.execute(db.select(Message)).scalars()
        list_messages = [message.to_dict() for message in messages]
        return make_response(list_messages)
    elif request.method == 'POST':
        data = request.json
        new_message = Message(body=data['body'], username=data['username'])
        db.session.add(new_message)
        db.session.commit()
        return make_response(new_message.to_dict(), 201)

@app.route('/messages/<int:id>', methods=["PATCH", "DELETE"])
def messages_by_id(id):
    if request.method == 'PATCH':
        message = db.session.execute(db.select(Message).filter_by(id=id)).scalar_one()
        data = request.get_json() if request.is_json else request.form.to_dict()
        for attr, value in data.items():
            if hasattr(message, attr):
                setattr(message, attr, value)
        db.session.commit()
        return make_response(message.to_dict(),202)
    if request.method == 'DELETE':
        message = db.session.execute(db.select(Message).filter_by(id=id)).scalar_one()
        db.session.delete(message)
        db.session.commit()
        response_body = {
            "delete_successful": True,
            "message": "Message deleted."
        }
        return make_response(response_body)

    

if __name__ == '__main__':
    app.run(port=5555)
