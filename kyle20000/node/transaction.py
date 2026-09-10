import hashlib
import json

from node.wallet import Wallet


class Transaction:
    def __init__(
        self,
        sender,
        recipient,
        amount,
        nonce,
        public_key=None
    ):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.nonce = nonce
        self.public_key = public_key
        self.signature = None

    def to_dict(self, include_signature=True):
        data = {
            "sender": self.sender,
            "public_key": self.public_key,
            "recipient": self.recipient,
            "amount": self.amount,
            "nonce": self.nonce
        }

        if include_signature:
            data["signature"] = self.signature

        return data

    def serialize(self):
        return json.dumps(
            self.to_dict(include_signature=False),
            sort_keys=True,
            separators=(",", ":")
        )

    def transaction_hash(self):
        return hashlib.sha256(
            self.serialize().encode("utf-8")
        ).hexdigest()

    def sign(self, wallet):
        if wallet.address != self.sender:
            raise ValueError(
                "wallet does not own sender address"
            )

        self.public_key = wallet.public_key

        self.signature = wallet.sign(
            self.serialize()
        )

    def verify(self):
        if not self.signature:
            return False

        if not self.public_key:
            return False

        # Make sure the public key actually belongs
        # to the sender address.
        if Wallet.verify_address(
            self.public_key
        ) != self.sender:
            return False

        return Wallet.verify(
            self.public_key,
            self.serialize(),
            self.signature
        )