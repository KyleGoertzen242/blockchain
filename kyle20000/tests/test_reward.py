from node.block import Block
from node.blockchain import Blockchain
from node.mining import proof_of_work


blockchain = Blockchain()

print("=== Kyle20000 Reward Test ===")

block = Block(
    index=1,
    previous_hash=blockchain.latest_block().calculate_hash(),
    transactions=[],
    miner="TEST-MINER",
    reward=1,
    difficulty=3
)

proof_of_work(block)

print("\nCorrect reward:")
print(block.reward)

valid, message = blockchain.validate_block(block)

print("Valid:", valid)
print("Message:", message)

print("\nChanging reward to 2 KyleCoins...")

block.reward = 2

valid, message = blockchain.validate_block(block)

print("Valid:", valid)
print("Message:", message)