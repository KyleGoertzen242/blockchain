from node.blockchain import Blockchain
from node.mining import mine_block
from node.wallet import Wallet
from node.transaction import Transaction


blockchain = Blockchain()

miner = Wallet()
alice = Wallet()
bob = Wallet()

print("=== Kyle20000 Mining Test ===")

print("\nMiner:")
print(miner.address)

print("\nAlice:")
print(alice.address)

print("\nBob:")
print(bob.address)


# Give Alice testnet funds.
blockchain.credit(alice.address, 1000)

print("\nAlice starting balance:")
print(blockchain.get_balance(alice.address))


# Create a transaction.
transaction = Transaction(
    sender=alice.address,
    recipient=bob.address,
    amount=100,
    nonce=0
)

transaction.sign(alice)

print("\nTransaction signature valid:")
print(transaction.verify(alice.public_key))


# Validate transaction.
valid, message = blockchain.validate_transaction(
    transaction,
    alice.public_key
)

print("\nTransaction validation:")
print(valid, message)


# Mine the transaction into a block.
block = mine_block(
    blockchain,
    [transaction],
    miner.address
)

print("\nBlock mined!")
print("Block index:", block.index)
print("Nonce:", block.nonce)
print("Hash:", block.calculate_hash())


# Add block.
blockchain.add_block(block)

# Apply transaction.
blockchain.apply_transaction(transaction)

print("\nAlice balance:")
print(blockchain.get_balance(alice.address))

print("\nBob balance:")
print(blockchain.get_balance(bob.address))

print("\nBlockchain valid:")
print(blockchain.validate())

print("\nProof-of-Work valid:")
print(
    block.calculate_hash().startswith(
        "0" * block.difficulty
    )
)