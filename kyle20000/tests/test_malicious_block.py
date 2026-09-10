from node.blockchain import Blockchain
from node.mining import mine_block
from node.transaction import Transaction
from node.wallet import Wallet


blockchain = Blockchain()

sender = Wallet()
recipient = Wallet()
miner = Wallet()

print("=== Kyle20000 Malicious Block Test ===")


# First mine 1 KyleCoin to the sender.
print("\nMining funding block...")

funding_block = mine_block(
    blockchain,
    [],
    sender.address
)

blockchain.add_block(funding_block)

print("Sender balance:")
print(blockchain.get_balance(sender.address))


# Create a legitimate transaction.
transaction = Transaction(
    sender=sender.address,
    recipient=recipient.address,
    amount=1,
    nonce=0
)

transaction.sign(sender)

print("\nLegitimate transaction:")
print(transaction.verify())


# Mine the legitimate transaction.
valid_block = mine_block(
    blockchain,
    [transaction],
    miner.address
)

print("\nLegitimate block validation:")

valid, message = blockchain.validate_block(
    valid_block
)

print("Valid:", valid)
print("Message:", message)


# Now create another transaction but do NOT sign it.
fake_transaction = Transaction(
    sender=sender.address,
    recipient=miner.address,
    amount=1,
    nonce=0
)

print("\nFake transaction signature:")
print(fake_transaction.signature)


# Put the fake transaction into a mined block.
malicious_block = mine_block(
    blockchain,
    [fake_transaction],
    miner.address
)

print("\nMalicious block validation:")

valid, message = blockchain.validate_block(
    malicious_block
)

print("Valid:", valid)
print("Message:", message)