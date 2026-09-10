from node.blockchain import Blockchain
from node.consensus import (
    chain_work,
    choose_chain,
    same_genesis
)
from node.mining import mine_block


def main():
    chain_a = Blockchain()

    chain_b = Blockchain()

    print(
        "Same genesis:",
        same_genesis(
            chain_a,
            chain_b
        )
    )

    block_a = mine_block(
        blockchain=chain_a,
        transactions=[],
        miner_address="MINER-A"
    )

    chain_a.add_block(
        block_a
    )

    block_b = mine_block(
        blockchain=chain_b,
        transactions=[],
        miner_address="MINER-B"
    )

    chain_b.add_block(
        block_b
    )

    print(
        "Chain A blocks:",
        len(chain_a.chain)
    )

    print(
        "Chain B blocks:",
        len(chain_b.chain)
    )

    print(
        "Chain A work:",
        chain_work(chain_a)
    )

    print(
        "Chain B work:",
        chain_work(chain_b)
    )

    print(
        "Same genesis after fork:",
        same_genesis(
            chain_a,
            chain_b
        )
    )

    # Give Chain B another block.
    block_b2 = mine_block(
        blockchain=chain_b,
        transactions=[],
        miner_address="MINER-B"
    )

    chain_b.add_block(
        block_b2
    )

    print(
        "Chain B blocks after extension:",
        len(chain_b.chain)
    )

    print(
        "Chain B work after extension:",
        chain_work(chain_b)
    )

    selected = choose_chain(
        chain_b,
        chain_a
    )

    print(
        "Higher-work chain selected:",
        selected is chain_b
    )


if __name__ == "__main__":
    main()