from flask import Flask, jsonify
from flask_pymongo import PyMongo 
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config  

import os


app = Flask(__name__)
app.config.from_object(Config)  
print(f"MongoDB URI: {app.config.get('MONGO_URI')}")


mongo = PyMongo(app) 
if mongo.db is None:
    print("MongoDB connection failed!")
else:
    print("MongoDB connected successfully!")

jwt = JWTManager(app)
CORS(app)

from routes.auth_routes import auth_bp
from routes.fir_routes import fir_bp
from routes.case_routes import case_bp


app.register_blueprint(auth_bp)
app.register_blueprint(fir_bp)
app.register_blueprint(case_bp)

@app.route("/", methods=["GET"])
def hello():
    return jsonify({"message": "Hello, World!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port, debug=True)
