import os
import time
import requests
from google import genai

# --- تنظیمات Gemini (کلیدهای چرخشی) ---
GEMINI_KEYS = [
    "AQ.Ab8RN6KgPtXVqlewAUNIEFSMbL0sKDaBn7HIYXHvmCjD89e5RQ",
    "AQ.Ab8RN6KxMC69YosMxNf2iDotkUsdui1i5LfzT51A4hAHBw5ajA",
    "AQ.Ab8RN6KapMbwjh5_rVBNPS16HsZW3DqBA1z6LPl-ePSK1M_BHw"
]
current_key_idx = 0

def get_ai_client():
    global current_key_idx
    key = GEMINI_KEYS[current_key_idx]
    current_key_idx = (current_key_idx + 1) % len(GEMINI_KEYS)
    # استفاده از SDK جدید گوگل
    return genai.Client(api_key=key)

# --- تنظیمات Toobit ---
BASE_URL = "https://api.toobit.com"

# --- موتور Paper Trading ---
virtual_balance = 1000.0
active_positions = []
MAX_POSITIONS = 2

def get_top_50_tickers():
    try:
        url = f"{BASE_URL}/api/v1/ticker/24hr"
        res = requests.get(url, timeout=10).json()
        usdt_pairs = [item for item in res if item['symbol'].endswith('USDT')][:50]
        return usdt_pairs
    except Exception as e:
        print(f"❌ خطا در دریافت داده‌های بازار توبیت: {e}")
        return []

def analyze_with_gemini(symbol, sample_price):
    client = get_ai_client()
    prompt = f"""
    شما یک معامله‌گر حرفه‌ای نوسان‌گیری (Scalper) هستید.
    جفت‌ارز: {symbol} | قیمت لحظه‌ای: {sample_price}
    
    لطفاً بررسی کنید آیا وضعیت برای ورود آنی مناسب است؟
    پاسخ را فقط در قالب JSON با این کلیدها ارسال کن:
    {{
        "decision": "BUY" یا "SELL" یا "WAIT",
        "entry_price": {sample_price},
        "stop_loss": حد_ضرر_پیشنهادی,
        "take_profit": حد_سود_پیشنهادی,
        "reason": "دلیل کوتاه به فارسی"
    }}
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"⚠️ خطا در استعلام از Gemini: {e}")
        return None

def main_loop():
    print("==================================================")
    print("🚀 ربات اسکنر نوسان‌گیری توبیت (Paper Trading)")
    print("==================================================")
    
    tickers = get_top_50_tickers()
    if not tickers:
        print("❌ هیچ ارزی یافت نشد. ارتباط اینترنت یا API را بررسی کنید.")
        return

    print(f"📊 ۵۰ ارز برتر دریافت شد. شروع بررسی 3 ارز اول...\n")
    
    for coin in tickers[:3]:
        symbol = coin['symbol']
        price = coin['lastPrice']
        print(f"🔍 در حال آنالیز {symbol} (قیمت: ${price})...")
        
        analysis = analyze_with_gemini(symbol, price)
        if analysis:
            print(f"🤖 پاسخ هوش مصنوعی:\n{analysis}\n")
        time.sleep(1)

if __name__ == "__main__":
    try:
        main_loop()
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
    
    print("\n==================================================")
    input("برای خروج، کلید Enter را روی کیبورد فشار دهید...")
