import json
import os

from .block import Block


BLOCKCHAIN_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "blockchain.json"
)


def ensure_data_directory():
    os.makedirs(
        os.path.dirname(BLOCKCHAIN_FILE),
        exist_ok=True
    )


def save_blockchain(blockchain):
    ensure_data_directory()

    data = [
        block.to_dict()
        for block in blockchain.chain
    ]

    temporary_file = BLOCKCHAIN_FILE + ".tmp"

    with open(temporary_file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            sort_keys=True
        )

    os.replace(
        temporary_file,
        BLOCKCHAIN_FILE
    )


def load_blockchain():
    if not os.path.exists(BLOCKCHAIN_FILE):
        return None

    with open(
        BLOCKCHAIN_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    chain = []

    for item in data:
        block = Block(
            index=item["index"],
            previous_hash=item["previous_hash"],
            transactions=item["transactions"],
            timestamp=item["timestamp"],
            nonce=item["nonce"],
            difficulty=item["difficulty"],
            miner=item["miner"],
            reward=item["reward"]
        )

        chain.append(block)

    return chain