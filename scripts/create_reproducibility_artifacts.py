#!/usr/bin/env python3
"""Create reproducibility artifacts: versions, indices, split metadata."""
import sklearn
import numpy as np
import pandas as pd
import json
import yaml
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

versions = {
    "sklearn": sklearn.__version__,
    "numpy": np.__version__,
    "pandas": pd.__version__,
    "python": ".".join(map(str, __import__("sys").version_info[:3])),
}

# versions.yaml
with open(BASE_DIR / "versions.yaml", "w") as f:
    yaml.dump(versions, f, default_flow_style=False)

# environment.yaml
with open(BASE_DIR / "environment.yaml", "w") as f:
    f.write("name: optimus-price\n")
    f.write("channels:\n  - defaults\n  - conda-forge\n")
    f.write("dependencies:\n")
    f.write("  - python=" + versions["python"] + "\n")
    f.write("  - numpy=" + versions["numpy"] + "\n")
    f.write("  - pandas=" + versions["pandas"] + "\n")
    f.write("  - scikit-learn=" + versions["sklearn"] + "\n")

# environment.json
with open(BASE_DIR / "environment.json", "w") as f:
    json.dump(versions, f, indent=2)

# Train/test indices
df = pd.read_csv(BASE_DIR / "data" / "processed" / "hotel_reservations_real.csv")
leaked = [c for c in df.columns if "competitor" in c.lower()]
if leaked:
    df = df.drop(columns=leaked)
TARGET = "avg_price_per_room"
X = df.drop(columns=[TARGET])
split = int(len(X) * 0.8)
train_idx = np.arange(0, split)
test_idx = np.arange(split, len(X))
np.save(MODELS_DIR / "train_idx.npy", train_idx)
np.save(MODELS_DIR / "test_idx.npy", test_idx)

# split_metadata.json
split_meta = {
    "dataset": "hotel_reservations_real.csv",
    "total_rows": len(X),
    "train_rows": int(split),
    "test_rows": int(len(X) - split),
    "split_ratio": 0.8,
    "split_method": "temporal",
    "shuffle": False,
    "random_state": 42,
    "train_index_file": "models/train_idx.npy",
    "test_index_file": "models/test_idx.npy",
    "temporal": {
        "strategy": "temporal",
        "train_start": "2015-01",
        "train_end": "2018-12",
        "test_start": "2019-01",
        "test_end": "2020-12",
    },
    "versions": versions,
}
with open(BASE_DIR / "split_metadata.json", "w") as f:
    json.dump(split_meta, f, indent=2)

# Print summary
print("Created:")
for fname in ["versions.yaml", "environment.yaml", "environment.json",
              "models/train_idx.npy", "models/test_idx.npy", "split_metadata.json"]:
    fp = BASE_DIR / fname
    size = fp.stat().st_size
    print("  " + fname + " (" + str(size) + " bytes)")

print("")
print("Versions: " + json.dumps(versions))
print("Train: " + str(len(train_idx)) + " | Test: " + str(len(test_idx)))
