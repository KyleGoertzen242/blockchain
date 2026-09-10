from node.blockchain import Blockchain
from node.mining import mine_block
from node.transaction import Transaction
from node.wallet import Wallet


blockchain = Blockchain()

sender = Wallet()
recipient = Wallet()
miner = Wallet()

print("=== Kyle20000 Duplicate Transaction Test ===")


# Give sender 1 KyleCoin.
funding_block = mine_block(
    blockchain,
    [],
    sender.address
)

blockchain.add_block(funding_block)


# Create and sign one transaction.
transaction = Transaction(
    sender=sender.address,
    recipient=recipient.address,
    amount=1,
    nonce=0
)

transaction.sign(sender)

print("\nOriginal transaction valid:")
print(
    blockchain.validate_transaction(transaction)
)


# Mine the transaction once.
first_block = mine_block(
    blockchain,
    [transaction],
    miner.address
)

blockchain.add_block(first_block)

print("\nFirst transaction block accepted.")

print(
    "Blockchain valid:",
    blockchain.validate()
)


# Try to put the exact same transaction
# into another block.
duplicate_block = mine_block(
    blockchain,
    [transaction],
    miner.address
)

print("\nTrying to add duplicate transaction...")

valid, message = blockchain.validate_block(
    duplicate_block
)

print("Valid:", valid)
print("Message:", message)