from nacl.signing import SigningKey, VerifyKey
import hashlib
import base64


class Wallet:
    def __init__(self, signing_key=None):
        if signing_key is None:
            self.signing_key = SigningKey.generate()
        else:
            self.signing_key = signing_key

        self.verify_key = self.signing_key.verify_key

    @classmethod
    def from_private_key(cls, private_key):
        signing_key = SigningKey(
            base64.b64decode(private_key)
        )

        return cls(
            signing_key=signing_key
        )

    @property
    def private_key(self):
        return base64.b64encode(
            bytes(self.signing_key)
        ).decode("utf-8")

    @property
    def public_key(self):
        return base64.b64encode(
            bytes(self.verify_key)
        ).decode("utf-8")

    @property
    def address(self):
        public_key = bytes(self.verify_key)

        return hashlib.sha256(
            public_key
        ).hexdigest()

    def sign(self, message):
        if isinstance(message, str):
            message = message.encode("utf-8")

        signature = self.signing_key.sign(
            message
        ).signature

        return base64.b64encode(
            signature
        ).decode("utf-8")

    @staticmethod
    def verify(
        public_key,
        message,
        signature
    ):
        try:
            verify_key = VerifyKey(
                base64.b64decode(public_key)
            )

            if isinstance(message, str):
                message = message.encode("utf-8")

            verify_key.verify(
                message,
                base64.b64decode(signature)
            )

            return True

        except Exception:
            return False

    @staticmethod
    def verify_address(public_key):
        public_key_bytes = base64.b64decode(
            public_key
        )

        return hashlib.sha256(
            public_key_bytes
        ).hexdigest()