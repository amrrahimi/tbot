import os
import time
import requests
import google.generativeai as genai

# --- تنظیمات Gemini ---
GEMINI_KEYS = [
    "AQ.Ab8RN6KgPtXVqlewAUNIEFSMbL0sKDaBn7HIYXHvmCjD89e5RQ",
    "AQ.Ab8RN6KxMC69YosMxNf2iDotkUsdui1i5LfzT51A4hAHBw5ajA",
    "AQ.Ab8RN6KapMbwjh5_rVBNPS16HsZW3DqBA1z6LPl-ePSK1M_BHw"
]
current_key_idx = 0

def get_ai_model():
    global current_key_idx
    key = GEMINI_KEYS[current_key_idx]
    genai.configure(api_key=key)
    current_key_idx = (current_key_idx + 1) % len(GEMINI_KEYS)
    return genai.GenerativeModel('gemini-1.5-flash')

# --- تنظیمات Toobit ---
BASE_URL = "https://api.toobit.com"

# --- موتور Paper Trading ---
virtual_balance = 1000.0
active_positions = []
MAX_POSITIONS = 2

def get_top_50_tickers():
    try:
        url = f"{BASE_URL}/api/v1/ticker/24hr"
        res = requests.get(url).json()
        usdt_pairs = [item for item in res if item['symbol'].endswith('USDT')][:50]
        return usdt_pairs
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return []

def analyze_with_gemini(symbol, candles_summary):
    model = get_ai_model()
    prompt = f"""
    شما یک معامله‌گر حرفه‌ای نوسان‌گیری (Scalper) هستید.
    جفت‌ارز: {symbol}
    تغییرات قیمت اخیر: {candles_summary}
    
    لطفاً بررسی کنید آیا وضعیت برای ورود آنی مناسب است؟
    پاسخ را فقط در قالب JSON با این کلیدها ارسال کن:
    {{
        "decision": "BUY" یا "SELL" یا "WAIT",
        "entry_price": قیمت_ورودی,
        "stop_loss": حد_ضرر,
        "take_profit": حد_سود,
        "reason": "دلیل کوتاه به فارسی"
    }}
    """
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return response.text
    except Exception as e:
        return None

def main_loop():
    print("🚀 ربات اسکنر نوسان‌گیری در حالت Paper Trading فعال شد...")
    tickers = get_top_50_tickers()
    print(f"📊 لیست ۵۰ ارز برتر دریافت شد. تعداد: {len(tickers)}")
    
    # نمونه اجرای اسکن
    for coin in tickers[:5]: # تست ۵ ارز اول
        print(f"در حال بررسی {coin['symbol']}...")
        # در این بخش داده‌ها پردازش شده و به Gemini ارسال می‌شوند

if __name__ == "__main__":
    main_loop()
