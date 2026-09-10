import json
import os

from .wallet import Wallet


WALLET_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "wallet.json"
)


def save_wallet(wallet):
    os.makedirs(
        os.path.dirname(WALLET_FILE),
        exist_ok=True
    )

    data = {
        "private_key": wallet.private_key,
        "public_key": wallet.public_key,
        "address": wallet.address
    }

    with open(
        WALLET_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=2
        )


def load_wallet():
    if not os.path.exists(WALLET_FILE):
        return None

    with open(
        WALLET_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    return data