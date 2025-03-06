from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database import mongo

fir_bp = Blueprint("fir", __name__)

@fir_bp.route("/fir/register", methods=["POST"])
@jwt_required()
def register_fir():
    data = request.json
    fir = {
        "complainant_name": data["complainant_name"],
        "aadhar": data["aadhar"],
        "contact": data["contact"],
        "description": data["description"],
        "status": "Pending",
    }
    mongo.db.firs.insert_one(fir)
    return jsonify({"message": "FIR registered successfully"}), 201

@fir_bp.route("/fir/list", methods=["GET"])
@jwt_required()
def list_firs():
    firs = list(mongo.db.firs.find({}, {"_id": 0}))
    return jsonify(firs), 200
