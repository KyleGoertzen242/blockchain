import json
import os

from .block import Block


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_DIRECTORY = os.path.dirname(
    os.path.dirname(__file__)
)

DATA_DIRECTORY = os.path.join(
    PROJECT_DIRECTORY,
    "data"
)

LEGACY_BLOCKCHAIN_FILE = os.path.join(
    DATA_DIRECTORY,
    "blockchain.json"
)


def get_node_data_directory(port):
    """
    Each node gets its own persistent directory.

    Example:

        data/
            node-5001/
                blockchain.json
            node-5002/
                blockchain.json
            node-5003/
                blockchain.json
    """

    return os.path.join(
        DATA_DIRECTORY,
        f"node-{port}"
    )


def get_blockchain_file(port):
    return os.path.join(
        get_node_data_directory(port),
        "blockchain.json"
    )


def ensure_data_directory(port):
    os.makedirs(
        get_node_data_directory(port),
        exist_ok=True
    )


# --------------------------------------------------
# Serialization
# --------------------------------------------------

def block_from_dict(data):
    return Block(
        index=data["index"],
        previous_hash=data["previous_hash"],
        transactions=data["transactions"],
        timestamp=data["timestamp"],
        nonce=data["nonce"],
        difficulty=data["difficulty"],
        miner=data["miner"],
        reward=data["reward"]
    )


def blocks_from_data(data):
    if not isinstance(data, list):
        raise ValueError(
            "blockchain database must contain a list"
        )

    chain = []

    for item in data:

        if not isinstance(item, dict):
            raise ValueError(
                "invalid block in blockchain database"
            )

        chain.append(
            block_from_dict(item)
        )

    return chain


# --------------------------------------------------
# Save
# --------------------------------------------------

def save_blockchain(blockchain, port):
    """
    Save this node's blockchain.

    Every node has its own file so the three local
    development nodes cannot overwrite each other's
    databases.
    """

    ensure_data_directory(port)

    blockchain_file = get_blockchain_file(port)
    temporary_file = blockchain_file + ".tmp"

    data = [
        block.to_dict()
        for block in blockchain.chain
    ]

    with open(
        temporary_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            sort_keys=True
        )

        f.flush()
        os.fsync(
            f.fileno()
        )

    # Atomic replacement.
    os.replace(
        temporary_file,
        blockchain_file
    )


# --------------------------------------------------
# Load
# --------------------------------------------------

def load_blockchain(port):
    """
    Load this node's blockchain.

    If the node does not have its own database yet,
    the old shared blockchain.json is used as a
    migration source.

    The old file is NOT deleted.

    This means existing coins/blocks are preserved
    when upgrading the database system.
    """

    node_file = get_blockchain_file(port)

    # ----------------------------------------------
    # Preferred: node-specific database
    # ----------------------------------------------

    if os.path.exists(node_file):

        with open(
            node_file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        return blocks_from_data(data)

    # ----------------------------------------------
    # Migration: old shared database
    # ----------------------------------------------

    if os.path.exists(
        LEGACY_BLOCKCHAIN_FILE
    ):

        with open(
            LEGACY_BLOCKCHAIN_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        return blocks_from_data(data)

    # ----------------------------------------------
    # No blockchain yet
    # ----------------------------------------------

    return None
