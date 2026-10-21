import os
import sys
import time
import requests
from google import genai

# فعال‌سازی انکودینگ UTF-8 برای نمایش درست زبان فارسی در ترمینال ویندوز
if sys.platform == "win32":
    try:
        os.system("chcp 65001 > nul")
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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
    return genai.Client(api_key=key)

# --- تنظیمات Toobit ---
BASE_URL = "https://api.toobit.com"

def get_top_50_tickers():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        url = f"{BASE_URL}/api/v1/ticker/24hr"
        response = requests.get(url, headers=headers, timeout=10)
        
        # بررسی وضعیت پاسخ سرور
        if response.status_code != 200:
            print(f"❌ خطا در اتصال به توبیت! کد وضعیت سرور: {response.status_code}")
            return []
            
        res = response.json()
        usdt_pairs = [item for item in res if item.get('symbol', '').endswith('USDT')][:50]
        return usdt_pairs
    except requests.exceptions.RequestException as e:
        print(f"❌ خطای شبکه یا فیلترینگ در اتصال به توبیت: {e}")
        return []
    except Exception as e:
        print(f"❌ خطای پردازش داده‌های توبیت: {e}")
        return []

def analyze_with_gemini(symbol, sample_price):
    try:
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
        print("\n⚠️ هیچ ارزی دریافت نشد. لطفاً اتصال اینترنت یا ابزار تغییر IP را بررسی کنید.")
        return

    print(f"📊 {len(tickers)} ارز برتر دریافت شد. شروع بررسی ۳ ارز اول...\n")
    
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
