"""
Script d'entraînement du modèle NLP.
Encapsule la logique du notebook text_modeling.ipynb.
"""
import pandas as pd
import numpy as np
import pickle
import json
import os
import argparse
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", type=str, default="data/synthetic/consultation_notes.csv")
    parser.add_argument("--output-dir", type=str, default="ml_models/text")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Chargement
    df = pd.read_csv(args.data_path)
    category_to_label = {"normal": 0, "cardio": 1, "metabolic": 2, "infectious": 3}
    label_to_category = {v: k for k, v in category_to_label.items()}
    df["label_encoded"] = df["category"].map(category_to_label)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        df["note"], df["label_encoded"],
        test_size=args.test_size, random_state=args.seed,
        stratify=df["label_encoded"]
    )

    # Entraînement
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2), max_features=5000,
            sublinear_tf=True, strip_accents="unicode"
        )),
        ("clf", LogisticRegression(
            max_iter=1000, C=1.0,
            multi_class="multinomial", solver="lbfgs",
            random_state=args.seed
        ))
    ])
    pipeline.fit(X_train, y_train)

    # Évaluation
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)
    auc = roc_auc_score(y_test, y_proba, multi_class="ovr", average="macro")

    report = classification_report(
        y_test, y_pred, target_names=list(category_to_label.keys()), output_dict=True
    )

    print("📊 Résultats :")
    print(classification_report(y_test, y_pred, target_names=list(category_to_label.keys())))
    print(f"AUC macro : {auc:.4f}")

    # Sauvegarde modèle
    with open(f"{args.output_dir}/tfidf_logreg_classifier.pkl", "wb") as f:
        pickle.dump(pipeline, f)

    # Sauvegarde mapping labels
    with open(f"{args.output_dir}/label_mapping.json", "w") as f:
        json.dump({
            "label_to_category": label_to_category,
            "category_to_label": category_to_label
        }, f)

    # Sauvegarde métriques (pour DVC metrics)
    metrics = {
        "auc_macro": round(auc, 4),
        "f1_macro": round(report["macro avg"]["f1-score"], 4),
        "accuracy": round(report["accuracy"], 4)
    }
    with open(f"{args.output_dir}/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n Modèle et métriques sauvegardés dans {args.output_dir}/")


if __name__ == "__main__":
    main()