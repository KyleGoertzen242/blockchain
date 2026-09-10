from .transaction import Transaction


class Mempool:
    def __init__(self):
        self.transactions = {}

    def add_transaction(self, transaction):
        if not isinstance(
            transaction,
            Transaction
        ):
            raise ValueError(
                "invalid transaction"
            )

        transaction_id = (
            transaction.transaction_hash()
        )

        if transaction_id in self.transactions:
            raise ValueError(
                "transaction already in mempool"
            )

        for existing in self.transactions.values():

            if (
                existing.sender
                == transaction.sender
                and existing.nonce
                == transaction.nonce
            ):
                raise ValueError(
                    "conflicting transaction nonce"
                )

        self.transactions[
            transaction_id
        ] = transaction

        return transaction_id

    def remove_transaction(
        self,
        transaction_id
    ):
        self.transactions.pop(
            transaction_id,
            None
        )

    def get_transactions(self):
        return list(
            self.transactions.values()
        )

    def get_transaction_dicts(self):
        return [
            transaction.to_dict()
            for transaction in self.get_transactions()
        ]

    def contains(self, transaction_id):
        return (
            transaction_id
            in self.transactions
        )

    def has_sender_nonce(
        self,
        sender,
        nonce
    ):
        for transaction in self.transactions.values():

            if (
                transaction.sender == sender
                and transaction.nonce == nonce
            ):
                return True

        return False

    def clear_confirmed(
        self,
        blockchain
    ):
        confirmed = []

        for transaction_id in list(
            self.transactions.keys()
        ):

            if blockchain.transaction_exists(
                transaction_id
            ):
                confirmed.append(
                    transaction_id
                )

        for transaction_id in confirmed:
            self.remove_transaction(
                transaction_id
            )

        return confirmed

    def __len__(self):
        return len(
            self.transactions
        )