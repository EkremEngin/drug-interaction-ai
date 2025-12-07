import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

# ===========================
# 1) Veri setini yükle
# ===========================
df = pd.read_csv("data/synthetic_ddi.csv")

# metin birleştirme (drug1 + drug2 → "ibuprofen warfarin")
df["text"] = df["drug_1"].astype(str) + " " + df["drug_2"].astype(str)

X = df["text"]
y = df["severity"].astype(int)

# ===========================
# 2) Vectorizer
# ===========================
vectorizer = TfidfVectorizer(ngram_range=(1, 2))  # bigram ekledik
X_vec = vectorizer.fit_transform(X)

# ===========================
# 3) Model
# ===========================
model = LogisticRegression(max_iter=500, class_weight="balanced")
model.fit(X_vec, y)

# ===========================
# 4) Modeli kaydet
# ===========================
with open("models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("models/interaction_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Yeni model başarıyla eğitildi ve kaydedildi!")
