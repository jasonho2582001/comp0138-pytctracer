import json

with open("copilot-predictions/pyopenssl/class/pyopenssl_copilot_class_predictions.json", "r") as f:
    data = json.load(f)

with open("ground-truth-data/pyopenssl/class/pyopenssl_ground_truth_classes.json", "r") as f:
    ground_truth = json.load(f)

for key in ground_truth:
    if key not in data:
        print(f"Key {key} not found in data")

for key in data:
    if key not in ground_truth:
        print(f"Key {key} not found in ground truth")