from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import safe_str_cmp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

users_db = {}
contacts_db = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email in users_db:
        return jsonify({'message': 'User already exists'}), 409
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users_db[email] = hashed_password
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email not in users_db or not bcrypt.check_password_hash(users_db[email], password):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200

@app.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({
        'access_token': new_access_token
    }), 200

@app.route('/contacts', methods=['POST'])
@jwt_required()
def create_contact():
    current_user = get_jwt_identity()
    data = request.get_json()
    contact_id = len(contacts_db) + 1
    contact = {
        'id': contact_id,
        'name': data.get('name'),
        'email': data.get('email'),
        'phone': data.get('phone')
    }
    if current_user not in contacts_db:
        contacts_db[current_user] = []
    contacts_db[current_user].append(contact)
    return jsonify({'message': 'Contact created', 'contact': contact}), 201

@app.route('/contacts', methods=['GET'])
@jwt_required()
def get_contacts():
    current_user = get_jwt_identity()
    user_contacts = contacts_db.get(current_user, [])
    return jsonify({'contacts': user_contacts}), 200

@app.route('/contacts/<int:contact_id>', methods=['PUT'])
@jwt_required()
def update_contact(contact_id):
    current_user = get_jwt_identity()
    user_contacts = contacts_db.get(current_user, [])
    contact = next((c for c in user_contacts if c['id'] == contact_id), None)
    if not contact:
        return jsonify({'message': 'Contact not found'}), 404

    data = request.get_json()
    contact['name'] = data.get('name', contact['name'])
    contact['email'] = data.get('email', contact['email'])
    contact['phone'] = data.get('phone', contact['phone'])

    return jsonify({'message': 'Contact updated', 'contact': contact}), 200

@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
@jwt_required()
def delete_contact(contact_id):
    current_user = get_jwt_identity()
    user_contacts = contacts_db.get(current_user, [])
    contact = next((c for c in user_contacts if c['id'] == contact_id), None)
    if not contact:
        return jsonify({'message': 'Contact not found'}), 404

    user_contacts.remove(contact)
    return jsonify({'message': 'Contact deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
