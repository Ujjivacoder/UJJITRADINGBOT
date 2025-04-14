import os
import ccxt
import csv
import time
import random
from datetime import datetime
from telegram import Bot
from telegram.ext import Updater, CommandHandler

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("KUCOIN_API_KEY")
API_SECRET = os.getenv("KUCOIN_API_SECRET")
API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")

exchange = ccxt.kucoin({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'password': API_PASSPHRASE,
    'enableRateLimit': True,
})

symbol = 'DOGE/USDT'
amount = 4.7  # initial capital in USDT
profit_target_pct = 1.0  # 1%
stop_loss_pct = 0.5      # 0.5%

TRADE_LOG_FILE = "trade_log.csv"

async def send_telegram_message(message: str):
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        await app.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Telegram Error: {e}")

def log_trade(trade_type, symbol, price, amount, pnl):
    with open(TRADE_LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), trade_type, symbol, price, amount, pnl])

def fetch_price():
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

def execute_trade():
    global amount
    price = fetch_price()

    # Simulate small position sizing based on current capital
    usdt_balance = exchange.fetch_balance()['total'].get('USDT', 0)
    if usdt_balance < 1:
        print("💸 Not enough balance to trade.")
        return

    quantity = round(usdt_balance / price, 4)

    # Buy
    order = exchange.create_market_buy_order(symbol, quantity)
    buy_price = order['price']
    print(f"🟢 Bought {quantity} {symbol} at {buy_price}")
    time.sleep(5)

    # Monitor for sell
    while True:
        current_price = fetch_price()
        change_pct = ((current_price - buy_price) / buy_price) * 100

        if change_pct >= profit_target_pct:
            sell_order = exchange.create_market_sell_order(symbol, quantity)
            pnl = (current_price - buy_price) * quantity
            print(f"✅ Sold for Profit at {current_price}")
            log_trade('SELL', symbol, current_price, quantity, pnl)
            amount += pnl
            break

        elif change_pct <= -stop_loss_pct:
            sell_order = exchange.create_market_sell_order(symbol, quantity)
            pnl = (current_price - buy_price) * quantity
            print(f"❌ Stop Loss Triggered at {current_price}")
            log_trade('SELL', symbol, current_price, quantity, pnl)
            amount += pnl
            break

        time.sleep(5)

def setup_csv():
    if not os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Type', 'Symbol', 'Price', 'Amount', 'PnL'])

def run_bot():
    setup_csv()
    print("🤖 UJJITRADINGBOT Started.")
    try:
        while True:
            execute_trade()
            time.sleep(random.randint(30, 60))  # cooldown
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    run_bot()
