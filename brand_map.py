import json
import os

def load_brand_map():
    json_path = os.path.join("data", "brand_map.json")

    with open(json_path, "rb") as f:
        raw = f.read()

    # Tüm BOM tiplerini temizle
    raw = raw.replace(b'\xfe', b'').replace(b'\xff', b'').replace(b'\x00', b'')

    text = raw.decode("utf-8", errors="ignore")

    return json.loads(text)

brand_map = load_brand_map()
