import random
import re

SIDE_EFFECTS = {
    "GI_BLEED": [
        "Mide ağrısı",
        "Karında kramp",
        "Üst karında yanma",
        "Hazımsızlık",
        "Bulantı",
        "Kanlı kusma",
        "Kahverengi veya siyah dışkı",
        "Taze kırmızı rektal kanama",
        "Karında şişlik ve gerginlik",
        "İştah azalması",
        "Baş dönmesi",
        "Kolay morarma",
        "Burun kanaması",
        "Uzayan kanamalar",
        "Nefes darlığı ile birlikte göğüs ağrısı"
    ],
    "QT_PROLONG": [
        "Göğüs rahatsızlığı",
        "Kalpte çarpıntı hissi",
        "Hızlı nabız",
        "Yavaş nabız",
        "Düzensiz kalp atımı",
        "Nabızda atlama hissi",
        "Baş dönmesi",
        "Aniden göz kararması",
        "Bayılma hissi",
        "Kısa süreli bilinç kaybı",
        "Eforla nefes darlığı",
        "Soğuk terleme"
    ],
    "CNS": [
        "Aşırı uyku hali",
        "Gündüz uyuklama",
        "Sersemlik",
        "Denge kaybı",
        "Sarhoşluk hissi",
        "Yürürken yalpalama",
        "Reflekslerde yavaşlama",
        "Reaksiyonlarda gecikme",
        "Konuşma bozulması",
        "Bilinç bulanıklığı",
        "Hafıza güçlüğü",
        "Odaklanma zorluğu",
        "Baş dönmesi",
        "Şiddetli yorgunluk",
        "Nefes alıp vermede yavaşlama"
    ],
    "HEPATIC": [
        "Gözlerde sararma",
        "Ciltte sararma",
        "Karın sağ üst kadranda ağrı",
        "Karında dolgunluk",
        "İştahsızlık",
        "Bulantı",
        "Koyu renk idrar",
        "Açık renkli dışkı",
        "Genel halsizlik",
        "Çabuk yorulma",
        "Kas ağrısı",
        "Kas hassasiyeti",
        "Gece terlemesi",
        "Karaciğer bölgesinde hassasiyet"
    ]
}

ABBREVIATIONS = {
    "QT": "QT (kalbin elektriksel repolarizasyon süresi)",
    "EKG": "EKG (elektrokardiyogram)",
    "INR": "INR (kanın pıhtılaşma ölçümü)"
}

def expand_abbreviations(text):
    for short, long in ABBREVIATIONS.items():
        text = re.sub(rf"\b{short}\b", long, text)
    return text

MEKANIZMA_BASIT = {
    "GI_BLEED": "Bu kombinasyon mide ve bağırsaklarda kanama riskini artırabilir.",
    "QT_PROLONG": "Bu ilaçlar kalp ritmini etkileyerek ritim düzensizliğine yol açabilir.",
    "CNS": "Her iki ilaç birlikte alındığında beyin ve sinir sisteminin fazla baskılanmasına neden olabilir.",
    "HEPATIC": "Karaciğer üzerinde ek yük oluşturarak enzim değerlerinde yükselmeye yol açabilir."
}

MEKANIZMA_TEKNIK = {
    "GI_BLEED": "Gastrointestinal mukozada hasar ve pıhtılaşma yanıtının azalması kanama riskini artırabilir.",
    "QT_PROLONG": "QT aralığını uzatarak ventriküler aritmiler için zemin hazırlayabilir.",
    "CNS": "Santral sinir sistemi depresyonunu artırarak sedasyon ve solunum baskılanmasına yol açabilir.",
    "HEPATIC": "Hepatik metabolizmanın yavaşlaması ilaç birikimine ve karaciğer enzimlerinde yükselmeye neden olabilir."
}

YONETIM = {
    "GI_BLEED": {
        1: [
            "Mide ağrısı veya hafif siyah dışkı fark edilirse doktora danışılmalıdır."
        ],
        2: [
            "Uzayan kanama, belirgin siyah dışkı veya kanlı kusma durumunda acil değerlendirme önerilir."
        ],
        3: [
            "Bu kombinasyondan mümkünse kaçınılmalıdır.",
            "Kanama belirtilerinde acil müdahale ve pıhtılaşma testleri (INR) yapılmalıdır."
        ]
    },
    "QT_PROLONG": {
        1: [
            "Ara ara olan çarpıntı veya hafif baş dönmesi varlığında doktora bilgi verilmelidir."
        ],
        2: [
            "Yeni başlayan çarpıntı, göğüs rahatsızlığı veya bayılma hissinde EKG değerlendirmesi gerekir."
        ],
        3: [
            "QT uzatan ilaçların birlikte kullanımından kaçınılmalıdır.",
            "Kullanım zorunluysa EKG ile QTc takibi yapılmalıdır."
        ]
    },
    "CNS": {
        1: [
            "Uyku hali ve dengesizlik düşme riskini artırabilir; araç kullanırken dikkatli olunmalıdır."
        ],
        2: [
            "Belirgin sedasyon veya denge kaybı gelişirse doz azaltımı veya ilaç değişimi düşünülmelidir."
        ],
        3: [
            "Solunum baskılanması riski nedeniyle bu kombinasyondan kaçınılmalıdır.",
            "Şiddetli uyku hali veya nefes darlığında acil yardım gerekir."
        ]
    },
    "HEPATIC": {
        1: [
            "Sarılık, koyu idrar veya açıklanamayan halsizlik olursa doktorunuza başvurun."
        ],
        2: [
            "Karaciğer enzimlerinin düzenli izlenmesi ve kas ağrısı gelişirse değerlendirme önerilir."
        ],
        3: [
            "Belirgin hepatotoksisite riski nedeniyle kombinasyondan kaçınılmalıdır.",
            "Karaciğer fonksiyon testleri ve gerektiğinde görüntüleme yapılmalıdır."
        ]
    }
}

RISK_TEXT = {1: "düşük", 2: "orta", 3: "yüksek"}

SEVERITY_EFFECT_COUNT = {1: 3, 2: 5, 3: 7}

def pick_effects(category, severity):
    effects = SIDE_EFFECTS.get(category, [])
    n = SEVERITY_EFFECT_COUNT.get(severity, 3)
    if n > len(effects):
        n = len(effects)
    if n <= 0:
        return []
    return random.sample(effects, n)

def ul(items):
    return "".join(f"<li>{item}</li>" for item in items)

def generate(drug_a, drug_b, severity, source, style, category):
    if category not in SIDE_EFFECTS:
        category = "GI_BLEED"

    yan_etkiler = pick_effects(category, severity)
    mekanizma_basit = expand_abbreviations(MEKANIZMA_BASIT[category])
    mekanizma_tek = expand_abbreviations(MEKANIZMA_TEKNIK[category])
    risk = RISK_TEXT.get(severity, "belirsiz")
    yonetim_list = YONETIM[category].get(severity, [])
    yonetim_html = ul(yonetim_list)
    yanetki_html = ul(yan_etkiler)

    if style == 1:
        return f"""
<strong>{drug_a} + {drug_b}</strong><br>
<strong>Risk seviyesi:</strong> {risk}<br><br>
{mekanizma_basit}<br><br>
<strong>Olası Belirtiler:</strong>
<ul>{yanetki_html}</ul>
"""

    if style == 2:
        return f"""
<strong>{drug_a} + {drug_b}</strong><br>
<strong>Risk seviyesi:</strong> {risk}<br><br>
{mekanizma_basit}<br><br>
<strong>Olası Yan Etkiler:</strong>
<ul>{yanetki_html}</ul>
<strong>Klinik yaklaşım:</strong>
<ul>{yonetim_html}</ul>
"""

    if style == 3:
        return f"""
<strong>KOMBİNASYON:</strong> {drug_a} + {drug_b}<br>
<strong>RİSK SEVİYESİ:</strong> {risk}<br><br>
<strong>MEKANİZMA:</strong><br>
{mekanizma_tek}<br><br>
<strong>KLİNİK BULGULAR:</strong>
<ul>{yanetki_html}</ul>
<strong>KLİNİK YÖNETİM:</strong>
<ul>{yonetim_html}</ul>
"""

    return "Açıklama üretilemedi."
