import requests, json, datetime, os

# === CONFIG ===
CURRENCIES = ["USD", "EUR", "GBP"]
CRYPTO = ["bitcoin", "ethereum"]
BASE = "TRY"  # Türk Lirası bazlı
TODAY = datetime.datetime.now().strftime("%Y-%m-%d")

# === EXCHANGE RATES ===
fx_url = f"https://api.exchangerate.host/latest?base={BASE}"
fx_data = requests.get(fx_url).json()

# === CRYPTO ===
crypto_url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(CRYPTO)}&vs_currencies={BASE.lower()}"
crypto_data = requests.get(crypto_url).json()

# === COMBINE ===
output = {
    "date": TODAY,
    "base": BASE,
    "currency": {c: round(fx_data["rates"].get(c, 0), 2) for c in CURRENCIES},
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
