from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from database import mongo

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    existing_user = mongo.db.users.find_one({"email": data["email"]})
    
    if existing_user:
        return jsonify({"message": "User already registered, please log in"}), 400
    
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = {
        "name": data["name"],
        "email": data["email"],
        "password": hashed_password,
        "role": data["role"], 
    }

    mongo.db.users.insert_one(user)
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    user = mongo.db.users.find_one({"email": data["email"]})

    if user and bcrypt.check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
