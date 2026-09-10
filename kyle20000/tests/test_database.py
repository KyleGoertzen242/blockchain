from node.block import Block
from node.blockchain import Blockchain
from node.database import save_blockchain, load_blockchain


blockchain = Blockchain()

block = Block(
    index=1,
    previous_hash=blockchain.latest_block().calculate_hash(),
    transactions=[],
    miner="TEST-MINER",
    reward=50,
    difficulty=3
)

nonce = 0

while True:
    block.nonce = nonce

    if block.calculate_hash().startswith(
        "0" * block.difficulty
    ):
        break

    nonce += 1

blockchain.add_block(block)

save_blockchain(blockchain)

print("Blockchain saved.")

loaded_chain = load_blockchain()

print("Blockchain loaded.")

print("Chain valid before tampering:")

test_blockchain = Blockchain()
test_blockchain.chain = loaded_chain

print(test_blockchain.validate())

print("\nTampering with block reward...")

loaded_chain[1].reward = 5000000

print("Chain valid after tampering:")

test_blockchain.chain = loaded_chain

print(test_blockchain.validate())