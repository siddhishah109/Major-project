from flask import Flask ,jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from database import mongo
from config import Config

# Import routes
from routes.auth_routes import auth_bp
from routes.fir_routes import fir_bp
from routes.case_routes import case_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(fir_bp)
app.register_blueprint(case_bp)


@app.route("/", methods=["GET"])
def hello():
    return jsonify({"message": "Hello, World!"})

if __name__ == "__main__":
    app.run(debug=True)
