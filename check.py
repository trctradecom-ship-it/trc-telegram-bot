import os
import json
import requests
from web3 import Web3

# ==============================
# CONFIG FROM GITHUB SECRETS
# ==============================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

MIN_BALANCE = 1  # Minimum required tokens
DECIMALS = 18    # Your token decimals

# ==============================
# CONNECT TO POLYGON NETWORK
# ==============================

RPC_URL = "https://polygon-rpc.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# ==============================
# ERC20 ABI (balanceOf only)
# ==============================

abi = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=abi
)

# ==============================
# LOAD USERS
# ==============================

try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = []

print(f"Checking {len(users)} users...")

# ==============================
# CHECK BALANCES
# ==============================

for user in users:
    telegram_id = user.get("telegram_id")
    wallet = user.get("wallet")

    try:
        wallet = Web3.to_checksum_address(wallet)
        raw_balance = contract.functions.balanceOf(wallet).call()
        balance = raw_balance / (10 ** DECIMALS)

        print(f"User {telegram_id} balance: {balance}")

        if balance < MIN_BALANCE:
            print(f"Removing user {telegram_id} (low balance)")

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/banChatMember",
                json={
                    "chat_id": CHANNEL_ID,
                    "user_id": telegram_id
                }
            )

            # Unban immediately so user can rejoin later
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/unbanChatMember",
                json={
                    "chat_id": CHANNEL_ID,
                    "user_id": telegram_id
                }
            )

    except Exception as e:
        print(f"Error checking user {telegram_id}: {e}")

print("Check complete.")
