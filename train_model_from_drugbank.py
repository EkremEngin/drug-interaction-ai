import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

severity_map = {
    "minor": 1,
    "low": 1,
    "mild": 1,
    "moderate": 2,
    "major": 3,
    "severe": 3,
    "serious": 3,
    "contraindicated": 3
}

print("drug_interactions.json yükleniyor...")

with open("data/drug_interactions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = []
labels = []

print("Kayıtlar işleniyor...")

count = 0

for main_drug, block in data.items():
    if not isinstance(block, dict):
        continue
    inter_list = block.get("interactions", [])
    if not isinstance(inter_list, list):
        continue

    main = main_drug.strip().lower()
    if not main:
        continue

    for item in inter_list:
        d2 = item.get("drug", "")
        sev_raw = item.get("severity", "")

        if not isinstance(d2, str) or not isinstance(sev_raw, str):
            continue

        d2 = d2.strip().lower()
        sev_raw = sev_raw.strip().lower()

        if not d2:
            continue
        if sev_raw not in severity_map:
            continue

        text = f"{main} {d2}"
        texts.append(text)
        labels.append(severity_map[sev_raw])
        count += 1

print(f"Toplam {count} etkileşim örneği toplandı.")
print("TF-IDF vectorizer eğitiliyor...")

vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
X = vectorizer.fit_transform(texts)

print("Model eğitiliyor...")

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    n_jobs=-1
)

model.fit(X, labels)

print("Model ve vectorizer kaydediliyor...")

with open("models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("models/interaction_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✔ Eğitim tamamlandı. Yeni model models/ klasörüne yazıldı.")
