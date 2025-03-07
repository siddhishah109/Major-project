from flask import Blueprint, request, jsonify
from database import mongo

fir_bp = Blueprint("fir", __name__)

def get_next_fir_id():
    counter = mongo.db.counters.find_one_and_update(
        {"_id": "fir_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]

@fir_bp.route("/fir/register", methods=["POST"])
def register_fir():
    data = request.json
    fir = {
        "fir_id": get_next_fir_id(),
        "complainant_name": data["complainant_name"],
        "aadhar": data["aadhar"],
        "contact": data["contact"],
        "description": data["description"],
        "status": "Pending",
    }
    mongo.db.firs.insert_one(fir)
    return jsonify({"message": "FIR registered successfully", "fir_id": fir["fir_id"]}), 201

@fir_bp.route("/fir/list", methods=["GET"])
def list_firs():
    firs = list(mongo.db.firs.find({}, {"_id": 0}))
    return jsonify(firs), 200
