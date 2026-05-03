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
    df = df.dropna(subset=["label_encoded"]).copy()
    df["label_encoded"] = df["label_encoded"].astype(int)
    label_counts = df["label_encoded"].value_counts()
    if label_counts.empty or len(label_counts) < 2:
        raise ValueError(
            "Impossible d'entraîner le modèle : au moins deux classes sont nécessaires."
        )

    # Split
    stratify_labels = df["label_encoded"] if label_counts.min() >= 2 else None
    if stratify_labels is None:
        print("⚠️  Stratification désactivée : certaines classes ont moins de 2 exemples.")

    split_seed = args.seed
    for attempt in range(5):
        X_train, X_test, y_train, y_test = train_test_split(
            df["note"], df["label_encoded"],
            test_size=args.test_size, random_state=split_seed,
            stratify=stratify_labels
        )
        if len(np.unique(y_train)) >= 2:
            break
        stratify_labels = None
        split_seed += 1
    else:
        raise ValueError(
            "Impossible de créer un jeu d'entraînement avec au moins deux classes."
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
    label_order = [category_to_label[key] for key in category_to_label.keys()]
    target_names = list(category_to_label.keys())
    report = classification_report(
        y_test,
        y_pred,
        labels=label_order,
        target_names=target_names,
        output_dict=True,
        zero_division=0
    )
    model_labels = list(pipeline.named_steps["clf"].classes_)
    unique_test = np.unique(y_test)
    if len(unique_test) >= 2 and set(unique_test).issubset(set(model_labels)):
        auc = roc_auc_score(
            y_test,
            y_proba,
            multi_class="ovr",
            average="macro",
            labels=model_labels
        )
    else:
        print("⚠️  AUC macro non calculable (classes insuffisantes ou absentes).")
        auc = 0.0

    print("📊 Résultats :")
    print(classification_report(
        y_test,
        y_pred,
        labels=label_order,
        target_names=target_names,
        zero_division=0
    ))
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
