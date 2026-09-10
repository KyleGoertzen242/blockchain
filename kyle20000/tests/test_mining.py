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

print("Mining block...")
print("Starting nonce:", block.nonce)
print("Difficulty:", block.difficulty)

block_hash = proof_of_work(block)

print("\nBlock mined!")
print("Nonce:", block.nonce)
print("Hash:", block_hash)

print("\nProof of Work valid:")
print(verify_proof_of_work(block))