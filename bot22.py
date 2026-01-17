from telegram import Bot
import yfinance as yf
import ta
import json
import os

# ===== BOT DETAILS =====
BOT_TOKEN = "8378237274:AAESiyF2j6Ty6RqbeQFaJ8xU8b21YMYAjTQ"
CHAT_ID =  5687377167

# ===== SWING SETTINGS =====
STOCKS = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
RSI_BUY = 40
RSI_SELL = 60
DATA_FILE = "last_signals.json"  # store last signals

bot = Bot(token=BOT_TOKEN)

# Load last signals from file
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        last_signals = json.load(f)
else:
    last_signals = {}

for stock in STOCKS:
    try:
        data = yf.download(
            stock,
            period="6mo",
            interval="1d",
            progress=False
        )

        if data is None or data.empty:
            continue

        close_prices = data["Close"].squeeze()

        rsi_series = ta.momentum.RSIIndicator(close=close_prices, window=14).rsi()
        rsi = rsi_series.iloc[-1]

        # Determine signal
        if rsi < RSI_BUY:
            signal = "BUY"
        elif rsi > RSI_SELL:
            signal = "SELL"
        else:
            signal = "HOLD"

        # Check if signal changed
        last_signal = last_signals.get(stock)
        if signal != last_signal and signal != "HOLD":
            bot.send_message(
                chat_id=CHAT_ID,
                text=f"📊 SWING {signal}\nStock: {stock}\nRSI: {round(rsi,2)}"
            )
            last_signals[stock] = signal  # update last signal

    except Exception as e:
        print(f"Error in {stock}: {e}")

# Save updated signals
with open(DATA_FILE, "w") as f:
    json.dump(last_signals, f)

