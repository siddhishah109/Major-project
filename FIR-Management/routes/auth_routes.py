from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database import mongo

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = {
        "name": data["name"],
        "email": data["email"],
        "password": hashed_password,
        "role": data["role"],  # Citizen / Police / Admin
    }

    mongo.db.users.insert_one(user)
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    user = mongo.db.users.find_one({"email": data["email"]})

    if user and bcrypt.check_password_hash(user["password"], data["password"]):
        access_token = create_access_token(identity={"email": user["email"], "role": user["role"]})
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
