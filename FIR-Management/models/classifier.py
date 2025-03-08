import h5py
import json
import torch
from transformers import AutoModelForSequenceClassification

MODEL_NAME = "bert-base-uncased"

def load_model(model_path):
    """ Load the trained BERT model from the .h5 file """
    with h5py.File(model_path, 'r') as h5_file:
        config_str = h5_file['config'].attrs['config_str']
        config_dict = json.loads(config_str)

        # Ensure correct number of labels
        num_labels = config_dict.get("num_labels", 6)

        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=num_labels)

        state_dict = {key: torch.tensor(h5_file['weights'][key][:]) for key in h5_file['weights']}
        model.load_state_dict(state_dict)
        model.eval()

        label_mapping = {int(k): v for k, v in h5_file['labels'].attrs.items()}

    return model, label_mapping
