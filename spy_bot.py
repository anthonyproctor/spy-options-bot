
import os
import time
from webull import paper_webull

# Load credentials from environment variables
EMAIL = os.getenv("WEBULL_EMAIL")
PASSWORD = os.getenv("WEBULL_PASSWORD")
TRADING_PASSWORD = os.getenv("WEBULL_TRADING_PASSWORD")
DEVICE_NAME = os.getenv("WEBULL_DEVICE_NAME", "spy-bot")

# Initialize paper trading session
wb = paper_webull()
wb.login(EMAIL, PASSWORD, device_name=DEVICE_NAME)
wb.get_trade_token(TRADING_PASSWORD)

def get_spy_price():
    quote = wb.get_quote("SPY")
    return float(quote['close'])

def get_option_contract_id(strike_offset=2, expiry='2025-03-28'):
    options = wb.get_options("SPY")
    current_price = get_spy_price()
    target_strike = round(current_price + strike_offset)

    for contract in options['data']['options']:
        for option in contract['calls']:
            if option['strikePrice'] == target_strike and expiry in option['expirationDate']:
                return option['code'], option['askPrice']
    return None, None

def place_trade(contract_id, price_cap=1.30, quantity=2):
    option_quote = wb.get_option_quote(contract_id)
    ask = float(option_quote['askList'][0]['price'])

    if ask <= price_cap:
        print(f"Placing market order for {quantity} contracts at ask ${ask}")
        wb.place_option_order(
            option_id=contract_id,
            action='BUY_TO_OPEN',
            order_type='MKT',
            enforce='GTC',
            quant=quantity,
            price=ask  # Required cap value for MKT order
        )
        return ask
    else:
        print(f"Ask ${ask} exceeds cap ${price_cap}. No trade executed.")
        return None

def bot_loop():
    while True:
        try:
            contract_id, ask_price = get_option_contract_id()
            if contract_id:
                entry_price = place_trade(contract_id)
                if entry_price:
                    print(f"Trade entered at ${entry_price}")
                    # Add logic for monitoring and auto-exit here
                    time.sleep(1200)  # 20 minutes before exit logic
            else:
                print("No valid contract found.")
        except Exception as e:
            print("Error during loop:", str(e))

        time.sleep(60)  # Wait a minute before rechecking

if __name__ == "__main__":
    bot_loop()
