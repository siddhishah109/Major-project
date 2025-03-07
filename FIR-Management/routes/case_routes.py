from flask import Blueprint, request, jsonify
from bson import ObjectId
from database import mongo

case_bp = Blueprint("case", __name__)

@case_bp.route("/case/update-status/<fir_id>", methods=["PUT"])
def update_case_status(fir_id):
    try:
        data = request.json

        # Validate if ObjectId is correct
        if not ObjectId.is_valid(fir_id):
            return jsonify({"error": "Invalid FIR ID"}), 400

        # Find the FIR
        fir = mongo.db.firs.find_one({"_id": ObjectId(fir_id)})

        if not fir:
            return jsonify({"error": "FIR not found"}), 404

        # Update FIR status
        mongo.db.firs.update_one({"_id": ObjectId(fir_id)}, {"$set": {"status": data["status"]}})

        # Return updated FIR
        updated_fir = mongo.db.firs.find_one({"_id": ObjectId(fir_id)})
        updated_fir["_id"] = str(updated_fir["_id"])  # Convert ObjectId to string

        return jsonify({"message": "Case status updated", "updated_fir": updated_fir}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@case_bp.route("/case/my-firs", methods=["POST"])
def get_user_firs():
    try:
        # Get Aadhar number from request body
        data = request.json
        user_aadhar = data.get("aadhar")

        if not user_aadhar:
            return jsonify({"error": "Aadhar number is required"}), 400

        # Fetch FIRs where the complainant's Aadhar matches the provided Aadhar
        user_firs = list(mongo.db.firs.find({"aadhar": user_aadhar}))

        # Convert ObjectId to string for JSON response
        for fir in user_firs:
            fir["_id"] = str(fir["_id"])

        return jsonify({"my_firs": user_firs}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@case_bp.route("/case/stats", methods=["GET"])
def get_case_stats():
    try:
        total_cases = mongo.db.firs.count_documents({})
        completed_cases = mongo.db.firs.count_documents({"status": "Completed"})
        pending_cases = mongo.db.firs.count_documents({"status": "Pending"})

        return jsonify({
            "total_cases": total_cases,
            "completed_cases": completed_cases,
            "pending_cases": pending_cases
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500