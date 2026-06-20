import pandas as pd

# Load both sources
hf = pd.read_csv("data/hf_combined.csv")
manual = pd.read_csv("data/manual_samples.csv")

# Sanity checks
print("HF samples:", len(hf))
print("HF label distribution:\n", hf["label"].value_counts())
print()
print("Manual samples:", len(manual))
print("Manual category distribution:\n", manual["category"].value_counts())
print("Manual label distribution:\n", manual["label"].value_counts())
print()

# Check for overlap between HF and manual text (avoid leakage)
overlap = set(hf["text"]).intersection(set(manual["text"]))
print("Overlapping samples between HF and manual:", len(overlap))

# Save final sets
# train.csv = HF data only (binary label, used for week 2 detector training)
# eval.csv  = manual data only (categorized, used as held-out hard test set)
hf.to_csv("data/train.csv", index=False)
manual.to_csv("data/eval.csv", index=False)

print()
print("Done. train.csv and eval.csv saved to data/")
