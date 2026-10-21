import time
import requests
from google import genai

# --- 1. Gemini AI Setup (Key Rotation) ---
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

# --- 2. Free Global Market Data Fetcher ---
def get_top_50_crypto():
    """
    Fetches Top 50 Cryptocurrencies live data globally (TradingView / CoinMarketCap standard)
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 50,
        'page': 1,
        'sparkline': False
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[!] Server returned status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"[!] Network Error: {e}")
        return []

# --- 3. Gemini Scalping Analysis ---
def analyze_with_gemini(symbol, price, change_24h):
    try:
        client = get_ai_client()
        prompt = f"""
        You are an expert crypto scalper trader.
        Symbol: {symbol.upper()}USDT
        Current Price: ${price}
        24h Price Change: {change_24h}%
        
        Analyze if this coin is good for an immediate scalp trade.
        Respond ONLY in JSON format:
        {{
            "decision": "BUY", "SELL", or "WAIT",
            "entry_price": {price},
            "stop_loss": calculated_stop_loss_price,
            "take_profit": calculated_take_profit_price,
            "reason": "Short explanation of the setup"
        }}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[!] Gemini AI Error: {e}")
        return None

# --- 4. Main Engine (Paper Trading) ---
def main_loop():
    print("==================================================")
    print("      CRYPTO SCALPER BOT - PAPER TRADING          ")
    print("==================================================")
    print("[+] Connecting to Global Crypto Data Center...")
    
    coins = get_top_50_crypto()
    if not coins:
        print("[!] Failed to fetch market data. Please check internet connection.")
        return

    print(f"[+] Successfully loaded TOP {len(coins)} Coins.")
    print("[+] Scanning Top 3 Coins for Scalp Signals...\n")
    
    for coin in coins[:3]:
        symbol = coin['symbol'].upper() + "USDT"
        price = coin['current_price']
        change = coin['price_change_percentage_24h']
        
        print(f"[*] Analyzing {symbol} | Price: ${price} | 24h Change: {change:.2f}%")
        
        analysis = analyze_with_gemini(symbol, price, change)
        if analysis:
            print(f"[🤖 AI Decision]:\n{analysis}\n")
        time.sleep(1)

if __name__ == "__main__":
    try:
        main_loop()
    except Exception as e:
        print(f"\n[!] Unexpected Error: {e}")
    
    print("==================================================")
    input("Press Enter to close window...")
