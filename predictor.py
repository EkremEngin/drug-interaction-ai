import json
import pickle
import itertools
import re
from brand_map import brand_map
from rapidfuzz import fuzz, process
from explanation_engine import generate as generate_explanation

DEBUG = True

# -----------------------------
# MODEL & DATA YÜKLEME
# -----------------------------
with open("models/interaction_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("models/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# JSON dosyası artık GitHub/Render'da olmadığı için boş dict kullanıyoruz.
# Bu, DrugBank verisi yoksa sistemin sorunsuz fallback yapmasını sağlar.
interaction_data = {}
interaction_data_norm = {}

generic_names_norm = set()
brand_map_norm = {k.lower(): v for k, v in brand_map.items()}


# -----------------------------
# TEMEL TEMİZLEME
# -----------------------------
def normalize_phrase(s: str) -> str:
    s = s.lower().strip().replace("-", " ")
    return " ".join(s.split())


def preprocess_input(text: str) -> str:
    text = text.lower()
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9çğıöşü\s]", " ", text)
    return " ".join(text.split())


def fuzzy_match_drug(word, candidates, threshold=82):
    match = process.extractOne(word, candidates, scorer=fuzz.ratio)
    if not match:
        return None
    name, score, _ = match
    return name if score >= threshold else None


# Alias map
ALIAS_MAP = {
    "varfarin": "warfarin",
    "varfarine": "warfarin",
    "klaritromisin": "clarithromycin",
    "claritromisin": "clarithromycin",
    "azitromisin": "azithromycin",
    "omeprasol": "omeprazole",
    "omezprazol": "omeprazole",
    "rofeks": "dexketoprofen",
    "rofex": "dexketoprofen",
}


# -----------------------------
# İLAÇ ÇIKARMA MOTORU
# -----------------------------
def extract_drugs_from_text(text: str):
    cleaned = preprocess_input(text)
    tokens = cleaned.split()
    n = len(tokens)

    found = []
    used = set()

    # Aday havuzu: sadece brand_map çünkü JSON artık yok
    all_candidates = list(brand_map_norm.keys()) + list(brand_map_norm.values())

    for i in range(n):
        for size in (3, 2, 1):
            if i + size > n:
                continue

            chunk = " ".join(tokens[i:i + size])
            key = normalize_phrase(chunk)

            if key in used:
                continue

            # 1) Alias
            if key in ALIAS_MAP:
                found.append(ALIAS_MAP[key])
                used.add(key)
                continue

            # 2) Brand isimleri → generic
            if key in brand_map_norm:
                found.append(brand_map_norm[key])
                used.add(key)
                continue

            # 3) Fuzzy
            fuzzy = fuzzy_match_drug(key, all_candidates, threshold=80)
            if fuzzy:
                base = brand_map_norm.get(fuzzy, fuzzy)
                found.append(base)
                used.add(fuzzy)

    # Tekilleştir
    result = []
    seen = set()
    for item in found:
        drug = normalize_phrase(item)
        if drug not in seen:
            seen.add(drug)
            result.append(drug)

    return result


# -----------------------------
# DRUGBANK FALLBACK
# -----------------------------
def get_drugbank_entry(a, b):
    return None  # JSON artık yok → fallback davranışı


# -----------------------------
# MODEL TAHMİNİ
# -----------------------------
def predict_pair(a, b):
    vec = vectorizer.transform([f"{a.lower()} {b.lower()}"])
    pred = model.predict(vec)[0]
    return str(pred)


def severity_score_from_label(s):
    if "3" in s:
        return 3
    if "2" in s:
        return 2
    if "1" in s:
        return 1
    return 0


# -----------------------------
# OVERRIDE SİSTEMLERİ
# -----------------------------
CRITICAL_OVERRIDE = {
    frozenset(["warfarin", "aspirin"]),
    frozenset(["warfarin", "ibuprofen"]),
    frozenset(["warfarin", "naproxen"]),
    frozenset(["warfarin", "clopidogrel"]),
    frozenset(["warfarin", "clarithromycin"]),
    frozenset(["warfarin", "azithromycin"]),
    frozenset(["simvastatin", "clarithromycin"]),
    frozenset(["rivaroxaban", "ibuprofen"]),
}

LOW_RISK_OVERRIDE = {
    frozenset(["paracetamol", "ibuprofen"]),
    frozenset(["paracetamol", "omeprazole"]),
    frozenset(["paracetamol", "simvastatin"]),
    frozenset(["omeprazole", "ibuprofen"]),
}

CLASS_INTERACTION = {
    tuple(sorted(["NSAID", "VKA"])): 3,
    tuple(sorted(["NSAID", "DOAC"])): 3,   # SSAID typo düzeltildi
    tuple(sorted(["Statin", "Makrolid"])): 3,
    tuple(sorted(["Makrolid", "VKA"])): 3,
    tuple(sorted(["Benzo", "Opioid"])): 3,
    tuple(sorted(["NSAID", "SSRI"])): 2,
    tuple(sorted(["Statin", "VKA"])): 2,
    tuple(sorted(["Makrolid", "DOAC"])): 2,
    tuple(sorted(["NSAID", "PPI"])): 1,
}


# -----------------------------
# SINIFLANDIRMA
# -----------------------------
def classify_drug(name: str) -> str:
    n = name.lower()
    if n in {"ibuprofen", "naproxen", "diclofenac", "dexketoprofen"}:
        return "NSAID"
    if n in {"paracetamol"}:
        return "Analjezik"
    if n in {"omeprazole", "pantoprazole", "esomeprazole"}:
        return "PPI"
    if n in {"simvastatin", "atorvastatin"}:
        return "Statin"
    if n in {"clarithromycin", "azithromycin", "erythromycin"}:
        return "Makrolid"
    if n in {"warfarin"}:
        return "VKA"
    if n in {"rivaroxaban", "apixaban"}:
        return "DOAC"
    if n in {"sertraline"}:
        return "SSRI"
    if n in {"alprazolam", "diazepam"}:
        return "Benzo"
    if n in {"tramadol", "codeine"}:
        return "Opioid"
    return "Diğer"


# -----------------------------
# KATEGORİ → AÇIKLAMA MOTORU
# -----------------------------
def determine_category(a, b):
    c1, c2 = classify_drug(a), classify_drug(b)
    pair = {c1, c2}

    if {"NSAID", "VKA"} == pair:
        return "GI_BLEED"
    if {"NSAID", "DOAC"} == pair:
        return "GI_BLEED"

    if {"Makrolid", "VKA"} == pair:
        return "QT_PROLONG"

    if {"Statin", "Makrolid"} == pair:
        return "HEPATIC"

    if {"Benzo", "Opioid"} == pair:
        return "CNS"

    return "GI_BLEED"


def apply_class_override(a, b, sev):
    c1, c2 = classify_drug(a), classify_drug(b)
    key = tuple(sorted([c1, c2]))
    if key in CLASS_INTERACTION:
        sev = max(sev, CLASS_INTERACTION[key])
    return sev


def apply_critical_override(a, b, sev):
    if frozenset([a, b]) in CRITICAL_OVERRIDE:
        return 3
    return sev


def apply_low_risk_override(a, b, sev):
    if sev == 3:
        return sev
    if frozenset([a, b]) in LOW_RISK_OVERRIDE:
        return 1
    return sev


# -----------------------------
# DİNAMİK ÖZET
# -----------------------------
def generate_dynamic_summary(style, results):
    major = sum(1 for r in results if r["severity"] == "3")
    moderate = sum(1 for r in results if r["severity"] == "2")
    mild = sum(1 for r in results if r["severity"] == "1")
    return f"Toplam {major} yüksek, {moderate} orta, {mild} hafif risk bulundu."


# -----------------------------
# ANA API FONKSİYONU
# -----------------------------
def predict_interactions(text: str, style: int = 1):
    drugs = extract_drugs_from_text(text)
    if len(drugs) < 1:
        return {"found_drugs": [], "pairs": [], "summary": "Metinden ilaç bulunamadı."}

    pairs = list(itertools.combinations(drugs, 2))
    results = []

    for a, b in pairs:
        sev = severity_score_from_label(predict_pair(a, b))
        sev = apply_critical_override(a, b, sev)
        sev = apply_class_override(a, b, sev)
        sev = apply_low_risk_override(a, b, sev)

        source = "[AI]"  # DrugBank JSON olmadığı için her zaman AI fallback

        category = determine_category(a, b)
        explanation = generate_explanation(a, b, sev, source, style, category)

        results.append({
            "drug_1": a,
            "drug_2": b,
            "severity": str(sev),
            "explanation": explanation
        })

    summary = generate_dynamic_summary(style, results)

    return {"found_drugs": drugs, "pairs": results, "summary": summary}


# -----------------------------
# TERMINAL TEST MODE
# -----------------------------
def main():
    text = input("Ne kullandığını yaz: ")
    out = predict_interactions(text, 1)

    print("\nBulunan ilaçlar:", out["found_drugs"])
    for p in out["pairs"]:
        print(f"{p['drug_1']} + {p['drug_2']} → {p['severity']}")
    print("\nÖzet:", out["summary"])


if __name__ == "__main__":
    main()
