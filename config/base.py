from dotenv import load_dotenv

import os

load_dotenv()

BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
BINANCE_API_SECRET_KEY = os.environ.get("BINANCE_API_SECRET_KEY")
