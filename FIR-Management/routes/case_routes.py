from bson import ObjectId
from flask import Blueprint, Response, request, jsonify,send_file
from werkzeug.utils import secure_filename
from gridfs import GridFS
import os
import io
from database import mongo

case_bp = Blueprint("case", __name__)

fs = GridFS(mongo.db)

@case_bp.route("/case/update/<int:fir_id>", methods=["PUT"])
def update_case(fir_id):
    try:
        update_fields = {}

        # Handle form-data (for files) or JSON input
        data = request.form if request.content_type.startswith('multipart/form-data') else request.json or {}
        if "status" in data:
            update_fields["status"] = data["status"]

        if "update" in data:
            update_fields.setdefault("updates", []).append(data["update"])

        # Handle file uploads
        uploaded_files = request.files.getlist("files")
        file_ids = []
        for file in uploaded_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_id = fs.put(file, filename=filename)  # Store file in GridFS
                file_ids.append(str(file_id))  # Convert ObjectId to string

        if file_ids:
            update_fields.setdefault("files", []).extend(file_ids)

        # If no valid data is provided, return an error
        if not update_fields:
            return jsonify({"error": "At least one field (status, update, or file) is required"}), 400

        # Find the FIR document
        fir = mongo.db.firs.find_one({"fir_id": fir_id})
        if not fir:
            return jsonify({"error": "FIR not found"}), 404

        # Prepare MongoDB update query
        update_query = {"$set": {}, "$push": {}}
        if "status" in update_fields:
            update_query["$set"]["status"] = update_fields["status"]
        if "updates" in update_fields:
            update_query["$push"]["updates"] = {"$each": update_fields["updates"]}
        if "files" in update_fields:
            update_query["$push"]["files"] = {"$each": update_fields["files"]}

        # Remove empty update fields
        update_query = {k: v for k, v in update_query.items() if v}

        # Perform update
        mongo.db.firs.update_one({"fir_id": fir_id}, update_query)

        # Retrieve updated FIR
        updated_fir = mongo.db.firs.find_one({"fir_id": fir_id})

        return jsonify({
            "message": "Case updated successfully",
            "updated_fir": {
                "fir_id": fir_id,
                "status": updated_fir.get("status"),
                "updates": updated_fir.get("updates", []),
                "files": updated_fir.get("files", [])  
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@case_bp.route("/case/download/<file_id>", methods=["GET"])
def download_file(file_id):
    try:
        # Convert file_id to ObjectId
        file_id = ObjectId(file_id)

        # Retrieve file from GridFS
        file_data = fs.get(file_id)
        if not file_data:
            return jsonify({"error": "File not found"}), 404

        # Return the file as a response
        return send_file(
            io.BytesIO(file_data.read()),
            mimetype=file_data.content_type,
            as_attachment=True,
            download_name=file_data.filename
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@case_bp.route("/files/<file_id>", methods=["GET"])
def view_file(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        if not file:
            return jsonify({"error": "File not found"}), 404

        content_type = file.content_type or "application/octet-stream"

       
        response = Response(io.BytesIO(file.read()), content_type=content_type)
        response.headers["Content-Disposition"] = f'inline; filename="{file.filename}"'

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@case_bp.route("/case/update-status/<int:fir_id>", methods=["PUT"])
def update_case_status(fir_id):
    try:
        data = request.json

        # Find the FIR by numeric FIR ID
        fir = mongo.db.firs.find_one({"fir_id": fir_id})

        if not fir:
            return jsonify({"error": "FIR not found"}), 404

        # Update FIR status
        mongo.db.firs.update_one({"fir_id": fir_id}, {"$set": {"status": data["status"]}})

        # Return updated FIR
        updated_fir = mongo.db.firs.find_one({"fir_id": fir_id})

        return jsonify({"message": "Case status updated", "updated_fir": updated_fir}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@case_bp.route("/case/add-update/<int:fir_id>", methods=["PUT"])
def add_case_update(fir_id):
    try:
        data = request.json
        new_update = data.get("update")

        if not new_update:
            return jsonify({"error": "Update field is required"}), 400
        fir = mongo.db.firs.find_one({"fir_id": fir_id})

        if not fir:
            return jsonify({"error": "FIR not found"}), 404

        mongo.db.firs.update_one(
            {"fir_id": fir_id},
            {"$push": {"updates": new_update}}
        )
        updated_fir = mongo.db.firs.find_one({"fir_id": fir_id})

        return jsonify({"message": "Case update added", "updated_fir": updated_fir}), 200

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