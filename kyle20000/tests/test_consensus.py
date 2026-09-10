from node.blockchain import Blockchain
from node.consensus import chain_work, is_chain_better
from node.mining import mine_block


def main():
    blockchain = Blockchain()

    original_work = chain_work(
        blockchain
    )

    block = mine_block(
        blockchain=blockchain,
        transactions=[],
        miner_address="TEST-MINER"
    )

    blockchain.add_block(block)

    new_work = chain_work(
        blockchain
    )

    print(
        "Original chain work:",
        original_work
    )

    print(
        "New chain work:",
        new_work
    )

    print(
        "New chain has more work:",
        new_work > original_work
    )

    candidate = Blockchain()

    candidate_block = mine_block(
        blockchain=candidate,
        transactions=[],
        miner_address="CANDIDATE-MINER"
    )

    candidate.add_block(
        candidate_block
    )

    print(
        "Candidate better than original:",
        is_chain_better(
            candidate,
            Blockchain()
        )
    )


if __name__ == "__main__":
    main()