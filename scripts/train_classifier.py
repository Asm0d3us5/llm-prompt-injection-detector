import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load training data (binary labeled HF data)
df = pd.read_csv("../data/train_v2.csv")
X_text = df["text"]
y = df["label"]

# Split off a small internal validation set (not the same as eval.csv)
X_train, X_val, y_train, y_val = train_test_split(
    X_text, y, test_size=0.15, random_state=42, stratify=y
)

# Vectorize
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),     # unigrams + bigrams catch phrases like "ignore previous"
    sublinear_tf=True,
    stop_words=None         # don't strip stopwords — "ignore" and "all" matter here
)
X_train_vec = vectorizer.fit_transform(X_train)
X_val_vec = vectorizer.transform(X_val)

# Train
clf = LogisticRegression(max_iter=1000, class_weight="balanced")
clf.fit(X_train_vec, y_train)

# Internal validation report
print("=== Internal validation (15% holdout of train_v2.csv) ===")
y_pred = clf.predict(X_val_vec)
print(classification_report(y_val, y_pred, target_names=["benign", "injection"]))

# Save model + vectorizer
joblib.dump(clf, "../models/classifier.pkl")
joblib.dump(vectorizer, "../models/vectorizer.pkl")
print("Saved model and vectorizer to ../models/")
