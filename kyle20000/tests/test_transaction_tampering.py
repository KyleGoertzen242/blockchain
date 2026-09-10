from node.wallet import Wallet
from node.transaction import Transaction


sender = Wallet()
recipient = Wallet()

transaction = Transaction(
    sender=sender.address,
    recipient=recipient.address,
    amount=100,
    nonce=0
)

transaction.sign(sender)

print("=== Kyle20000 Transaction Security Test ===")

print("\nOriginal transaction:")
print(transaction.to_dict())

print("\nOriginal signature valid:")
print(transaction.verify())

print("\nChanging amount from 100 to 1000...")

transaction.amount = 1000

print("Signature valid after amount change:")
print(transaction.verify())

print("\nRestoring amount to 100...")

transaction.amount = 100

print("Signature valid after restoring amount:")
print(transaction.verify())

print("\nChanging public key...")

attacker = Wallet()

transaction.public_key = attacker.public_key

print("Signature valid after public key change:")
print(transaction.verify())