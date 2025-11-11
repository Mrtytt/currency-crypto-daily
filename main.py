import subprocess
import requests, json, datetime, os
import matplotlib.pyplot as plt

# === CONFIG ===
BASE = "TRY"
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CHF"]
CRYPTO = ["bitcoin", "ethereum", "solana", "dogecoin"]
TODAY = datetime.datetime.now().strftime("%Y-%m-%d")

# === FETCH CURRENCY ===
fx_url = f"https://open.er-api.com/v6/latest/{BASE}"
fx_data = requests.get(fx_url).json()
if "rates" not in fx_data:
    raise Exception("Exchange rate data not found!")

# === FETCH CRYPTO ===
crypto_url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(CRYPTO)}&vs_currencies={BASE.lower()}"
crypto_data = requests.get(crypto_url).json()

# === PREPARE OUTPUT ===
output = {
    "date": TODAY,
    "base": BASE,
    "currency": {c: round(1 / fx_data["rates"].get(c, 1), 2) for c in CURRENCIES},
    "crypto": {k: v.get(BASE.lower(), 0) for k, v in crypto_data.items()}
}

# === SAVE DATA ===
os.makedirs("data/history", exist_ok=True)
with open(f"data/history/{TODAY}.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)
with open("data/latest.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

# === LOAD LAST 7 DAYS FOR TREND ===
history = []
dates = []
for i in range(7):
    d = (datetime.datetime.now() - datetime.timedelta(days=6 - i)).strftime("%Y-%m-%d")
    path = f"data/history/{d}.json"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            history.append(data)
            dates.append(d)

if history:
    # Grafik oluştur
    plt.figure(figsize=(8, 4))
    for key in ["USD", "EUR", "GBP"]:
        values = [h["currency"][key] for h in history if key in h["currency"]]
        plt.plot(dates[-len(values):], values, marker="o", label=key)
    plt.title("💵 Weekly Currency Trend (TRY)")
    plt.xlabel("Date")
    plt.ylabel("Price in TRY")
    plt.legend()
    plt.grid(alpha=0.3)
    os.makedirs("data", exist_ok=True)
    plt.tight_layout()
    plt.savefig("data/trend.png")
    plt.close()

# === BUILD README ===
readme = f"""# 💰 Daily Currency & Crypto Tracker
> Automatically updated every day — data sourced live from [open.er-api.com](https://open.er-api.com) and [CoinGecko](https://coingecko.com)

📅 **Date:** {TODAY}
🕒 **Updated at:** {datetime.datetime.now().strftime("%H:%M:%S")}

---

## 💵 Currencies (Base: {BASE})
| Currency | Rate (TRY) |
|-----------|------------|
{chr(10).join([f"| {c} | {output['currency'][c]} |" for c in CURRENCIES])}

## 🪙 Crypto
| Coin | Price (TRY) |
|------|--------------|
{chr(10).join([f"| {k.capitalize()} | {v} |" for k, v in output['crypto'].items()])}

---

## 📈 7-Day Trend (TRY)
![Trend Chart](data/trend.png)

✨ *This data updates automatically every day at 10:00 (TR Time).*
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("✅ Dashboard updated successfully!")

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"🔄 Manual update {TODAY}"], check=False)
    subprocess.run(["git", "push"], check=True)
    print("🚀 Changes pushed to GitHub successfully!")
except Exception as e:
    print("⚠️ Push failed:", e)