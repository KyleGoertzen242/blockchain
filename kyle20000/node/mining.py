from .block import Block
from .protocol import get_block_reward, MINIMUM_DIFFICULTY
from .transaction import Transaction


def proof_of_work(block):
    target = "0" * block.difficulty

    while True:
        block_hash = block.calculate_hash()

        if block_hash.startswith(target):
            return block_hash

        block.nonce += 1


def verify_proof_of_work(block):
    if block.difficulty < MINIMUM_DIFFICULTY:
        return False

    block_hash = block.calculate_hash()
    target = "0" * block.difficulty

    return block_hash.startswith(target)


def create_mining_block(blockchain, transactions, miner_address):
    latest = blockchain.latest_block()

    next_index = latest.index + 1

    return Block(
        index=next_index,
        previous_hash=latest.calculate_hash(),
        transactions=[
            transaction.to_dict()
            if isinstance(transaction, Transaction)
            else transaction
            for transaction in transactions
        ],
        miner=miner_address,
        reward=get_block_reward(next_index),
        difficulty=MINIMUM_DIFFICULTY
    )


def mine_block(blockchain, transactions, miner_address):
    block = create_mining_block(
        blockchain,
        transactions,
        miner_address
    )

    proof_of_work(block)

    if not verify_proof_of_work(block):
        raise ValueError(
            "mined block failed Proof-of-Work"
        )

    return block