import pandas as pd
from rule_engine import scan

df = pd.read_csv("../data/eval.csv")

results = []
for _, row in df.iterrows():
    result = scan(row["text"])
    results.append({
        "text": row["text"][:60],
        "true_label": row["label"],
        "true_category": row["category"],
        "predicted_flagged": result["flagged"],
        "predicted_category": result["category"],
    })

results_df = pd.DataFrame(results)

# Compare predicted flag vs true label
results_df["correct"] = (results_df["predicted_flagged"].astype(int) == results_df["true_label"])

print("=== Overall accuracy ===")
print(results_df["correct"].value_counts())
print()

print("=== False negatives (missed attacks) ===")
fn = results_df[(results_df["true_label"] == 1) & (results_df["predicted_flagged"] == False)]
print(fn[["text", "true_category"]].to_string(index=False))
print()

print("=== False positives (benign flagged as attack) ===")
fp = results_df[(results_df["true_label"] == 0) & (results_df["predicted_flagged"] == True)]
print(fp[["text", "predicted_category"]].to_string(index=False))

results_df.to_csv("../data/rule_engine_results.csv", index=False)
