# Kyle20000 protocol rules

INITIAL_BLOCK_REWARD = 1
MINIMUM_DIFFICULTY = 3


def get_block_reward(block_index):
    """
    Return the mining reward for a block.

    For the initial Kyle20000 protocol,
    every mined block receives 1 KyleCoin.
    """

    if block_index <= 0:
        return 0

    return INITIAL_BLOCK_REWARD