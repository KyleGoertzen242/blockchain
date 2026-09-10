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

print("Sender:")
print(sender.address)

print("\nRecipient:")
print(recipient.address)

print("\nTransaction before signing:")
print(transaction.to_dict())

transaction.sign(sender)

print("\nTransaction after signing:")
print(transaction.to_dict())

valid = transaction.verify()

print("\nSignature valid:", valid)