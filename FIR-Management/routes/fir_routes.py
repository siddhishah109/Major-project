from flask import Blueprint, request, jsonify
from database import mongo
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import text_to_word_sequence
import h5py

fir_bp = Blueprint("fir", __name__)

def build_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(input_dim=5000, output_dim=128, input_length=50), 
        tf.keras.layers.LSTM(64, return_sequences=True),
        tf.keras.layers.LSTM(64),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax')  
    ])
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

model = build_model()
model.load_weights("fir_classification_model.h5")  

def get_next_fir_id():
    counter = mongo.db.counters.find_one_and_update(
        {"_id": "fir_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]


def preprocess_text(text):
    words = text_to_word_sequence(text)  
    word_index = {word: i+1 for i, word in enumerate(set(words))}  
    sequence = [word_index[word] for word in words if word in word_index]  
    return sequence

@fir_bp.route("/fir/register", methods=["POST"])
def register_fir():
    data = request.json
    description = data.get("description", "")

  
    tokenized_description = preprocess_text(description)
    padded_description = pad_sequences([tokenized_description], maxlen=50)  

   
    prediction = model.predict(padded_description)
    predicted_category = np.argmax(prediction) 
    print("Predicted category:", predicted_category) 
    categories = ['theft', 'assault', 'fraud', 'cyber', 'sexual', 'domestic']
    category_label = categories[predicted_category] if 0 <= predicted_category < len(categories) else "Unknown"
    print("Mapped Category:", categories[predicted_category] if 0 <= predicted_category < len(categories) else "Unknown")

    fir = {
        "fir_id": get_next_fir_id(),
        "complainant_name": data.get("complainant_name"),
        "father_husband_name": data.get("father_husband_name"),
        "address": data.get("address"),
        "phone_number": data.get("phone_number"),
        "email": data.get("email"),
        "city": data.get("city"),
        "district": data.get("district"),
        "state": data.get("state"),
        "nature_of_offense": data.get("nature_of_offense"),
        "description": description,
        "details_of_witnesses": data.get("details_of_witnesses"),
        "aadhar_number": data.get("aadhar_number"),
        "status": "Pending",
        "predicted_category": category_label,  
    }

    mongo.db.firs.insert_one(fir)
    return jsonify({
    "message": "FIR registered successfully",
    "fir_id": int(fir["fir_id"]), 
    "category": category_label
}), 201

@fir_bp.route("/fir/list", methods=["GET"])
def list_firs():
    firs = list(mongo.db.firs.find({}, {"_id": 0}))
    return jsonify(firs), 200




# For model prediction when registering FIR



# from flask import Blueprint, request, jsonify
# from database import mongo
# from models.classifier import load_model

# fir_bp = Blueprint("fir", __name__)

# # Load FIR classification model
# MODEL_PATH = "fir_classification_model.h5"
# model, label_mapping = load_model(MODEL_PATH)

# def get_next_fir_id():
#     counter = mongo.db.counters.find_one_and_update(
#         {"_id": "fir_id"},
#         {"$inc": {"seq": 1}},
#         upsert=True,
#         return_document=True
#     )
#     return counter["seq"]

# @fir_bp.route("/fir/register", methods=["POST"])
# def register_fir():
#     data = request.json
#     category = predict_fir_category(data["description"])

#     fir = {
#         "fir_id": get_next_fir_id(),
#         "complainant_name": data["complainant_name"],
#         "aadhar": data["aadhar"],
#         "contact": data["contact"],
#         "description": data["description"],
#         "location": data["location"],
#         "category": category,
#         "status": "Pending",
#     }

#     mongo.db.firs.insert_one(fir)
#     return jsonify({"message": "FIR registered successfully", "fir_id": fir["fir_id"], "category": category}), 201

# @fir_bp.route("/fir/list", methods=["GET"])
# def list_firs():
#     firs = list(mongo.db.firs.find({}, {"_id": 0}))
#     return jsonify(firs), 200

# def predict_fir_category(text):
#     from transformers import AutoTokenizer
#     import torch

#     tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
#     inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

#     with torch.no_grad():
#         outputs = model(**inputs)
#         predicted_class = torch.argmax(outputs.logits, dim=1).item()

#     return label_mapping.get(predicted_class, "Unknown")
