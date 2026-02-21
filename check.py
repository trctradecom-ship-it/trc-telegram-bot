import json
import os
import requests
from web3 import Web3

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

RPC_URL = "https://polygon-rpc.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

abi = [{
    "constant": True,
    "inputs": [{"name": "_owner", "type": "address"}],
    "name": "balanceOf",
    "outputs": [{"name": "balance", "type": "uint256"}],
    "type": "function"
}]

contract = w3.eth.contract(
    address=Web3.toChecksumAddress(CONTRACT_ADDRESS),
    abi=abi
)

with open("settings.json") as f:
    settings = json.load(f)

required_amount = settings["required_tokens"] * (10 ** 18)

with open("users.json") as f:
    users = json.load(f)

updated_users = []

for user in users:
    wallet = user["wallet"]
    telegram_id = user["telegram_id"]

    try:
        balance = contract.functions.balanceOf(wallet).call()
    except:
        continue

    if balance >= required_amount:
        updated_users.append(user)
    else:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/banChatMember",
            data={"chat_id": CHANNEL_ID, "user_id": telegram_id}
        )
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/unbanChatMember",
            data={"chat_id": CHANNEL_ID, "user_id": telegram_id}
        )

with open("users.json", "w") as f:
    json.dump(updated_users, f, indent=2)
