from node.block import Block
from node.mining import proof_of_work, verify_proof_of_work


block = Block(
    index=1,
    previous_hash="0" * 64,
    transactions=[],
    miner="TEST-MINER",
    reward=50,
    difficulty=3
)

proof_of_work(block)

print("Original block:")
print("Hash:", block.calculate_hash())
print("Valid:", verify_proof_of_work(block))

block.reward = 5000000

print("\nAfter changing the reward:")
print("Hash:", block.calculate_hash())
print("Valid:", verify_proof_of_work(block))