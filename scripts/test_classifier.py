import pandas as pd
import joblib

clf = joblib.load("../models/classifier.pkl")
vectorizer = joblib.load("../models/vectorizer.pkl")

df = pd.read_csv("../data/manual_holdout.csv")
X_vec = vectorizer.transform(df["text"])

predictions = clf.predict(X_vec)
probabilities = clf.predict_proba(X_vec)[:, 1]  # probability of "injection" class

df["ml_predicted"] = predictions
df["ml_confidence"] = probabilities.round(3)
df["correct"] = (df["ml_predicted"] == df["label"])

print("=== Overall accuracy on eval.csv ===")
print(df["correct"].value_counts())
print()

print("=== False negatives (missed attacks) ===")
fn = df[(df["label"] == 1) & (df["ml_predicted"] == 0)]
print(fn[["text", "category", "ml_confidence"]].to_string(index=False))
print()

print("=== False positives (benign flagged as attack) ===")
fp = df[(df["label"] == 0) & (df["ml_predicted"] == 1)]
print(fp[["text", "ml_confidence"]].to_string(index=False))

df.to_csv("../data/ml_classifier_results.csv", index=False)
