from .protocol import MINIMUM_DIFFICULTY


def block_work(block):
    """
    Calculate simplified Proof-of-Work represented by a block.

    This is a prototype chainwork calculation.
    """

    if block.difficulty < MINIMUM_DIFFICULTY:
        return 0

    return 16 ** block.difficulty


def chain_work(blockchain):
    """
    Calculate cumulative Proof-of-Work for a blockchain.
    """

    total_work = 0

    for block in blockchain.chain:
        total_work += block_work(block)

    return total_work


def is_chain_better(candidate, current):
    """
    Return True when candidate has more cumulative
    Proof-of-Work than the current chain.
    """

    return chain_work(candidate) > chain_work(current)


def same_genesis(candidate, current):
    """
    Make sure both chains begin with the same genesis block.
    """

    if not candidate.chain:
        return False

    if not current.chain:
        return False

    return (
        candidate.chain[0].calculate_hash()
        == current.chain[0].calculate_hash()
    )


def choose_chain(candidate, current):
    """
    Select the valid higher-work chain.

    Returns:
        candidate if it should replace current
        current otherwise
    """

    if not candidate.validate():
        return current

    if not same_genesis(
        candidate,
        current
    ):
        return current

    if is_chain_better(
        candidate,
        current
    ):
        return candidate

    return current