from .block import Block
from .protocol import get_block_reward, MINIMUM_DIFFICULTY
from .transaction import Transaction
from .wallet import Wallet


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(
            index=0,
            previous_hash="0" * 64,
            transactions=[],
            timestamp=0,
            nonce=0,
            difficulty=MINIMUM_DIFFICULTY,
            miner="GENESIS",
            reward=0
        )

    def latest_block(self):
        return self.chain[-1]

    def get_balance(self, address):
        balances, _ = self.rebuild_state()
        return balances.get(address, 0)

    def get_nonce(self, address):
        _, nonces = self.rebuild_state()
        return nonces.get(address, 0)

    def rebuild_state(self):
        balances = {}
        nonces = {}

        for block in self.chain:
            if block.miner and block.reward > 0:
                balances[block.miner] = (
                    balances.get(block.miner, 0)
                    + block.reward
                )

            for transaction_data in block.transactions:
                sender = transaction_data["sender"]
                recipient = transaction_data["recipient"]
                amount = transaction_data["amount"]

                balances[sender] = (
                    balances.get(sender, 0)
                    - amount
                )

                balances[recipient] = (
                    balances.get(recipient, 0)
                    + amount
                )

                nonces[sender] = (
                    nonces.get(sender, 0)
                    + 1
                )

        return balances, nonces

    def transaction_exists(self, transaction_id):
        for block in self.chain:
            for transaction_data in block.transactions:
                try:
                    transaction = Transaction(
                        sender=transaction_data["sender"],
                        recipient=transaction_data["recipient"],
                        amount=transaction_data["amount"],
                        nonce=transaction_data["nonce"],
                        public_key=transaction_data["public_key"]
                    )

                    transaction.signature = (
                        transaction_data["signature"]
                    )

                    if transaction.transaction_hash() == transaction_id:
                        return True

                except (KeyError, TypeError):
                    continue

        return False

    def validate_transaction(self, transaction):
        if not isinstance(transaction, Transaction):
            return False, "invalid transaction"

        if not transaction.signature:
            return False, "transaction is not signed"

        if not transaction.public_key:
            return False, "transaction has no public key"

        if transaction.sender != Wallet.verify_address(
            transaction.public_key
        ):
            return False, "public key does not match sender"

        if not transaction.verify():
            return False, "invalid signature"

        if not isinstance(transaction.amount, int):
            return False, "amount must be an integer"

        if transaction.amount <= 0:
            return False, "invalid amount"

        if transaction.sender == transaction.recipient:
            return False, "sender and recipient cannot be the same"

        if self.transaction_exists(
            transaction.transaction_hash()
        ):
            return False, "transaction already exists"

        if transaction.nonce != self.get_nonce(
            transaction.sender
        ):
            return False, "invalid nonce"

        if self.get_balance(
            transaction.sender
        ) < transaction.amount:
            return False, "insufficient balance"

        return True, "valid"

    def validate_block(self, block):
        previous = self.latest_block()

        if block.index != previous.index + 1:
            return False, "invalid block index"

        if block.previous_hash != previous.calculate_hash():
            return False, "invalid previous hash"

        if block.difficulty < MINIMUM_DIFFICULTY:
            return False, "difficulty too low"

        if not block.calculate_hash().startswith(
            "0" * block.difficulty
        ):
            return False, "invalid proof of work"

        expected_reward = get_block_reward(
            block.index
        )

        if block.reward != expected_reward:
            return False, "invalid block reward"

        balances, nonces = self.rebuild_state()

        seen_transactions = set()

        for transaction_data in block.transactions:
            try:
                transaction = Transaction(
                    sender=transaction_data["sender"],
                    recipient=transaction_data["recipient"],
                    amount=transaction_data["amount"],
                    nonce=transaction_data["nonce"],
                    public_key=transaction_data["public_key"]
                )

                transaction.signature = (
                    transaction_data["signature"]
                )

            except (KeyError, TypeError):
                return False, "invalid transaction format"

            transaction_id = transaction.transaction_hash()

            if transaction_id in seen_transactions:
                return False, "duplicate transaction in block"

            if self.transaction_exists(transaction_id):
                return False, "transaction already exists"

            seen_transactions.add(transaction_id)

            if not transaction.signature:
                return False, "transaction is not signed"

            if not transaction.public_key:
                return False, "transaction has no public key"

            if transaction.sender != Wallet.verify_address(
                transaction.public_key
            ):
                return False, "public key does not match sender"

            if not transaction.verify():
                return False, "invalid transaction signature"

            if not isinstance(transaction.amount, int):
                return False, "transaction amount must be an integer"

            if transaction.amount <= 0:
                return False, "invalid transaction amount"

            if transaction.sender == transaction.recipient:
                return False, "sender and recipient cannot be the same"

            expected_nonce = nonces.get(
                transaction.sender,
                0
            )

            if transaction.nonce != expected_nonce:
                return False, "invalid transaction nonce"

            sender_balance = balances.get(
                transaction.sender,
                0
            )

            if sender_balance < transaction.amount:
                return False, "insufficient transaction balance"

            balances[transaction.sender] = (
                sender_balance - transaction.amount
            )

            balances[transaction.recipient] = (
                balances.get(
                    transaction.recipient,
                    0
                )
                + transaction.amount
            )

            nonces[transaction.sender] = (
                expected_nonce + 1
            )

        return True, "valid"

    def add_block(self, block):
        valid, message = self.validate_block(block)

        if not valid:
            raise ValueError(message)

        self.chain.append(block)

    def validate(self):
        balances = {}
        nonces = {}
        seen_transactions = set()

        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.index != previous.index + 1:
                return False

            if current.previous_hash != previous.calculate_hash():
                return False

            if current.difficulty < MINIMUM_DIFFICULTY:
                return False

            if not current.calculate_hash().startswith(
                "0" * current.difficulty
            ):
                return False

            expected_reward = get_block_reward(
                current.index
            )

            if current.reward != expected_reward:
                return False

            if current.miner and current.reward > 0:
                balances[current.miner] = (
                    balances.get(current.miner, 0)
                    + current.reward
                )

            for transaction_data in current.transactions:
                try:
                    transaction = Transaction(
                        sender=transaction_data["sender"],
                        recipient=transaction_data["recipient"],
                        amount=transaction_data["amount"],
                        nonce=transaction_data["nonce"],
                        public_key=transaction_data["public_key"]
                    )

                    transaction.signature = (
                        transaction_data["signature"]
                    )

                except (KeyError, TypeError):
                    return False

                transaction_id = transaction.transaction_hash()

                if transaction_id in seen_transactions:
                    return False

                seen_transactions.add(transaction_id)

                if not transaction.signature:
                    return False

                if not transaction.public_key:
                    return False

                if transaction.sender != Wallet.verify_address(
                    transaction.public_key
                ):
                    return False

                if not transaction.verify():
                    return False

                if not isinstance(transaction.amount, int):
                    return False

                if transaction.amount <= 0:
                    return False

                if transaction.sender == transaction.recipient:
                    return False

                expected_nonce = nonces.get(
                    transaction.sender,
                    0
                )

                if transaction.nonce != expected_nonce:
                    return False

                sender_balance = balances.get(
                    transaction.sender,
                    0
                )

                if sender_balance < transaction.amount:
                    return False

                balances[transaction.sender] = (
                    sender_balance
                    - transaction.amount
                )

                balances[transaction.recipient] = (
                    balances.get(
                        transaction.recipient,
                        0
                    )
                    + transaction.amount
                )

                nonces[transaction.sender] = (
                    expected_nonce + 1
                )

        return True