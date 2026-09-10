import hashlib
import json
import time


class Block:
    def __init__(
        self,
        index,
        previous_hash,
        transactions,
        timestamp=None,
        nonce=0,
        difficulty=1,
        miner=None,
        reward=0
    ):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.nonce = nonce
        self.difficulty = difficulty
        self.miner = miner
        self.reward = reward

    def to_dict(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "miner": self.miner,
            "reward": self.reward
        }

    def serialize(self):
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":")
        )

    def calculate_hash(self):
        return hashlib.sha256(
            self.serialize().encode("utf-8")
        ).hexdigest()