import pandas as pd
from scanner import hybrid_scan

df = pd.read_csv("../data/manual_holdout.csv")

results = []
for _, row in df.iterrows():
    result = hybrid_scan(row["text"])
    results.append({
        "text": row["text"][:60],
        "true_label": row["label"],
        "true_category": row["category"],
        "predicted_flagged": result["flagged"],
        "method": result["method"],
        "confidence": result["confidence"],
    })

results_df = pd.DataFrame(results)
results_df["correct"] = (results_df["predicted_flagged"].astype(int) == results_df["true_label"])

print("=== Hybrid scanner accuracy on manual_holdout.csv ===")
print(results_df["correct"].value_counts())
print()

print("=== False negatives ===")
fn = results_df[(results_df["true_label"] == 1) & (results_df["predicted_flagged"] == False)]
print(fn[["text", "true_category", "confidence"]].to_string(index=False))
print()

print("=== False positives ===")
fp = results_df[(results_df["true_label"] == 0) & (results_df["predicted_flagged"] == True)]
print(fp[["text", "method", "confidence"]].to_string(index=False))

results_df.to_csv("../data/hybrid_scanner_results.csv", index=False)
