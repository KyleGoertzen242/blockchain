from node.blockchain import Blockchain
from node.mining import mine_block
from node.transaction import Transaction
from node.wallet import Wallet


blockchain = Blockchain()

sender = Wallet()
recipient = Wallet()
miner = Wallet()

print("=== Kyle20000 Transaction Validation Test ===")

print("\nSender:")
print(sender.address)

print("\nRecipient:")
print(recipient.address)

print("\nMiner:")
print(miner.address)


# Create a signed transaction.
transaction = Transaction(
    sender=sender.address,
    recipient=recipient.address,
    amount=1,
    nonce=0
)

transaction.sign(sender)

print("\nTransaction:")
print(transaction.to_dict())

print("\nTransaction signature valid:")
print(transaction.verify())


# The sender needs funds before spending.
# For this test, we will create a valid mining
# reward first.
print("\nMining first block for the sender...")

funding_block = mine_block(
    blockchain,
    [],
    sender.address
)

blockchain.add_block(funding_block)

print("Funding block mined.")
print("Sender balance:", blockchain.get_balance(sender.address))


# Validate the transaction.
valid, message = blockchain.validate_transaction(
    transaction
)

print("\nTransaction validation:")
print("Valid:", valid)
print("Message:", message)


# Mine the transaction into the next block.
print("\nMining transaction...")

transaction_block = mine_block(
    blockchain,
    [transaction],
    miner.address
)

blockchain.add_block(transaction_block)

print("Transaction block mined.")

print("\nFinal balances:")
print("Sender:", blockchain.get_balance(sender.address))
print("Recipient:", blockchain.get_balance(recipient.address))
print("Miner:", blockchain.get_balance(miner.address))

print("\nBlockchain valid:")
print(blockchain.validate())