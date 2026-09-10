from node.block import Block
from node.blockchain import Blockchain


blockchain = Blockchain()

print("Genesis hash:")
print(blockchain.latest_block().calculate_hash())

block = Block(
    index=1,
    previous_hash=blockchain.latest_block().calculate_hash(),
    transactions=[
        {
            "type": "test",
            "amount": 100
        }
    ],
    miner="TEST-MINER",
    reward=50
)

blockchain.add_block(block)

print("\nBlockchain:")

for block in blockchain.chain:
    print(block.to_dict())
    print("Hash:", block.calculate_hash())

print("\nValid:", blockchain.validate())