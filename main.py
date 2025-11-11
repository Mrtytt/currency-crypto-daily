import requests
import json
import datetime
import os
import subprocess

# === CONFIG ===
CURRENCIES = ["USD", "EUR", "GBP"]
CRYPTO = ["bitcoin", "ethereum"]
BASE = "TRY"
TODAY = datetime.datetime.now().strftime("%Y-%m-%d")

# === EXCHANGE RATES ===
fx_url = f"https://api.exchangerate.host/latest?base={BASE}"
fx_resp = requests.get(fx_url)
if fx_resp.status_code != 200:
    raise Exception("❌ Exchange API request failed.")

fx_data = fx_resp.json()

# Bazı durumlarda "rates" anahtarı eksik olabilir
if "rates" not in fx_data:
    print("⚠️  'rates' not found in response, using fallback API...")
    # Alternatif API (Exchangerate-api.com - key gerekmez)
    fallback_url = "https://open.er-api.com/v6/latest/TRY"
    fx_data = requests.get(fallback_url).json()
    fx_data = {"rates": fx_data.get("rates", {})}

# === CRYPTO ===
crypto_url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(CRYPTO)}&vs_currencies={BASE.lower()}"
crypto_data = requests.get(crypto_url).json()

# === COMBINE ===
output = {
    "date": TODAY,
    "base": BASE,
    "currency": {c: round(1 / fx_data["rates"].get(c, 1), 2) for c in CURRENCIES},
    "crypto": {k: v.get(BASE.lower(), 0) for k, v in crypto_data.items()}
}

# === SAVE DATA ===
os.makedirs("data/history", exist_ok=True)
with open("data/latest.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)
with open(f"data/history/{TODAY}.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

# === UPDATE README ===
readme_template = f"""# 💰 Daily Currency & Crypto Tracker
Automatically updated every day with latest rates.

📅 **Date:** {TODAY}

## 💵 Currency (Base: {BASE})
| Currency | Rate |
|-----------|------|
{chr(10).join([f"| {c} | {output['currency'][c]} |" for c in CURRENCIES])}

## 🪙 Crypto
| Coin | Price ({BASE}) |
|------|----------------|
{chr(10).join([f"| {k.capitalize()} | {v} |" for k, v in output['crypto'].items()])}

---

📊 [View Full History](./data/history/)
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_template)

print("✅ Data updated successfully!")

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"🔄 Manual update {TODAY}"], check=False)
    subprocess.run(["git", "push"], check=True)
    print("🚀 Changes pushed to GitHub successfully!")
except Exception as e:
    print("⚠️ Push failed:", e)
