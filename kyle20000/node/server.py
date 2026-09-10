import json
import sys
import urllib.request
import urllib.error

from flask import Flask, jsonify, request
from flask_cors import CORS

from .blockchain import Blockchain
from .block import Block
from .mempool import Mempool
from .transaction import Transaction
from .mining import mine_block
from .consensus import choose_chain


app = Flask(__name__)
CORS(app)

blockchain = Blockchain()
mempool = Mempool()


# --------------------------------------------------
# Local development network
# --------------------------------------------------

DEFAULT_PORT = 5001

PEERS = {
    5001: [
        "http://127.0.0.1:5002",
        "http://127.0.0.1:5003"
    ],
    5002: [
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5003"
    ],
    5003: [
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5002"
    ]
}


def get_port():
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            pass

    return DEFAULT_PORT


PORT = get_port()


def get_peers():
    return PEERS.get(PORT, [])


def get_request_peer(peers):
    """
    Identify the local peer that sent the current request.

    This is suitable for the current three-node local
    development network.

    It should eventually be replaced with an authenticated
    peer identity/handshake for production networking.
    """

    remote_port = request.environ.get(
        "REMOTE_PORT"
    )

    if not remote_port:
        return None

    try:
        remote_port = int(remote_port)
    except ValueError:
        return None

    for peer in peers:
        try:
            peer_port = int(
                peer.rsplit(":", 1)[1]
            )
        except (ValueError, IndexError):
            continue

        if peer_port == remote_port:
            return peer

    return None


def broadcast(
    endpoint,
    payload,
    exclude_peer=None
):
    """
    Send a message to every configured peer except
    the peer that sent us the message.
    """

    results = []

    for peer in get_peers():

        if peer == exclude_peer:
            continue

        url = peer + endpoint

        try:
            data = json.dumps(
                payload
            ).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(
                req,
                timeout=3
            ) as response:

                body = response.read().decode(
                    "utf-8"
                )

                results.append({
                    "peer": peer,
                    "success": True,
                    "response": body
                })

        except Exception as error:

            results.append({
                "peer": peer,
                "success": False,
                "error": str(error)
            })

    return results


# --------------------------------------------------
# Serialization helpers
# --------------------------------------------------

def block_to_dict(block):
    return block.to_dict()


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


def blockchain_to_dict(blockchain_object):
    return [
        block_to_dict(block)
        for block in blockchain_object.chain
    ]


def blockchain_from_dict(data):
    candidate = Blockchain()

    candidate.chain = [
        block_from_dict(block)
        for block in data
    ]

    return candidate


# --------------------------------------------------
# Status
# --------------------------------------------------

@app.route("/status", methods=["GET"])
def status():

    latest = blockchain.latest_block()

    return jsonify({
        "node": PORT,
        "blocks": len(
            blockchain.chain
        ),
        "latest_block": latest.index,
        "latest_hash": latest.calculate_hash(),
        "mempool_size": len(mempool),
        "peers": get_peers()
    })


# --------------------------------------------------
# Peers
# --------------------------------------------------

@app.route("/peers", methods=["GET"])
def peers():

    return jsonify({
        "node": PORT,
        "peers": get_peers()
    })


@app.route("/ping", methods=["GET"])
def ping():

    return jsonify({
        "ok": True,
        "node": PORT
    })


@app.route("/peer-status", methods=["GET"])
def peer_status():

    results = []

    for peer in get_peers():

        try:
            with urllib.request.urlopen(
                peer + "/ping",
                timeout=3
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

                results.append({
                    "peer": peer,
                    "online": True,
                    "response": data
                })

        except Exception as error:

            results.append({
                "peer": peer,
                "online": False,
                "error": str(error)
            })

    return jsonify({
        "node": PORT,
        "peers": results
    })


# --------------------------------------------------
# Blockchain
# --------------------------------------------------

@app.route("/blockchain", methods=["GET"])
def get_blockchain():

    return jsonify({
        "blocks": blockchain_to_dict(
            blockchain
        )
    })


# --------------------------------------------------
# Mempool
# --------------------------------------------------

@app.route("/mempool", methods=["GET"])
def get_mempool():

    return jsonify({
        "transactions":
            mempool.get_transaction_dicts(),
        "count": len(mempool)
    })


# --------------------------------------------------
# Balance
# --------------------------------------------------

@app.route(
    "/balance/<address>",
    methods=["GET"]
)
def get_balance(address):

    return jsonify({
        "address": address,
        "balance": blockchain.get_balance(
            address
        ),
        "nonce": blockchain.get_nonce(
            address
        )
    })


# --------------------------------------------------
# Transaction validation helper
# --------------------------------------------------

def validate_transaction_for_mempool(
    transaction
):
    """
    Validate a transaction against both the
    confirmed blockchain and the current mempool.
    """

    valid, message = (
        blockchain.validate_transaction(
            transaction
        )
    )

    if not valid:
        return False, message

    if mempool.has_sender_nonce(
        transaction.sender,
        transaction.nonce
    ):
        return (
            False,
            "conflicting transaction nonce already in mempool"
        )

    return True, "valid"


# --------------------------------------------------
# Local transaction submission
# --------------------------------------------------

@app.route(
    "/transaction",
    methods=["POST"]
)
def submit_transaction():

    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return jsonify({
            "accepted": False,
            "reason": "invalid JSON"
        }), 400

    try:

        transaction = Transaction(
            sender=data["sender"],
            recipient=data["recipient"],
            amount=data["amount"],
            nonce=data["nonce"],
            public_key=data["public_key"]
        )

        transaction.signature = (
            data["signature"]
        )

    except (
        KeyError,
        TypeError
    ):

        return jsonify({
            "accepted": False,
            "reason": "invalid transaction format"
        }), 400

    valid, message = (
        validate_transaction_for_mempool(
            transaction
        )
    )

    if not valid:

        return jsonify({
            "accepted": False,
            "reason": message
        }), 400

    transaction_id = (
        mempool.add_transaction(
            transaction
        )
    )

    broadcast_results = broadcast(
        "/receive-transaction",
        transaction.to_dict()
    )

    return jsonify({
        "accepted": True,
        "transaction_id": transaction_id,
        "broadcast": broadcast_results
    })


# --------------------------------------------------
# Receive transaction from peer
# --------------------------------------------------

@app.route(
    "/receive-transaction",
    methods=["POST"]
)
def receive_transaction():

    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return jsonify({
            "accepted": False,
            "reason": "invalid JSON"
        }), 400

    try:

        transaction = Transaction(
            sender=data["sender"],
            recipient=data["recipient"],
            amount=data["amount"],
            nonce=data["nonce"],
            public_key=data["public_key"]
        )

        transaction.signature = (
            data["signature"]
        )

    except (
        KeyError,
        TypeError
    ):

        return jsonify({
            "accepted": False,
            "reason": "invalid transaction format"
        }), 400

    valid, message = (
        validate_transaction_for_mempool(
            transaction
        )
    )

    if not valid:

        return jsonify({
            "accepted": False,
            "reason": message
        }), 400

    transaction_id = (
        mempool.add_transaction(
            transaction
        )
    )

    sender_peer = get_request_peer(
        get_peers()
    )

    broadcast_results = broadcast(
        "/receive-transaction",
        transaction.to_dict(),
        exclude_peer=sender_peer
    )

    return jsonify({
        "accepted": True,
        "transaction_id": transaction_id,
        "broadcast": broadcast_results
    })


# --------------------------------------------------
# Mining
# --------------------------------------------------

@app.route(
    "/mine",
    methods=["POST"]
)
def mine():

    """
    Development-only mining endpoint.

    Production mining should use a real wallet
    and authenticated/local mining process.
    """

    miner_address = (
        "NODE-" + str(PORT)
    )

    transactions = (
        mempool.get_transactions()
    )

    block = mine_block(
        blockchain,
        transactions,
        miner_address
    )

    blockchain.add_block(
        block
    )

    mempool.clear_confirmed(
        blockchain
    )

    broadcast_results = broadcast(
        "/receive-block",
        block.to_dict()
    )

    return jsonify({
        "mined": True,
        "block": block.to_dict(),
        "broadcast": broadcast_results
    })


@app.route(
    "/mine-to/<address>",
    methods=["POST", "GET"]
)
def mine_to(address):

    """
    Development-only endpoint.

    Mines a block and assigns the protocol reward
    to the supplied wallet address.
    """

    transactions = (
        mempool.get_transactions()
    )

    block = mine_block(
        blockchain,
        transactions,
        address
    )

    blockchain.add_block(
        block
    )

    mempool.clear_confirmed(
        blockchain
    )

    broadcast_results = broadcast(
        "/receive-block",
        block.to_dict()
    )

    return jsonify({
        "mined": True,
        "miner": address,
        "reward": block.reward,
        "block": block.to_dict(),
        "broadcast": broadcast_results
    })


# --------------------------------------------------
# Receive block from peer
# --------------------------------------------------

@app.route(
    "/receive-block",
    methods=["POST"]
)
def receive_block():

    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):

        return jsonify({
            "accepted": False,
            "reason": "invalid JSON"
        }), 400

    try:

        block = block_from_dict(
            data
        )

    except (
        KeyError,
        TypeError,
        ValueError
    ):

        return jsonify({
            "accepted": False,
            "reason": "invalid block format"
        }), 400

    # Already have this exact block.
    for existing_block in blockchain.chain:

        if (
            existing_block.calculate_hash()
            == block.calculate_hash()
        ):
            return jsonify({
                "accepted": False,
                "reason": "block already exists"
            }), 200

    try:

        blockchain.add_block(
            block
        )

    except ValueError as error:

        return jsonify({
            "accepted": False,
            "reason": str(error)
        }), 400

    # Remove transactions that have now been
    # confirmed by the newly accepted block.
    mempool.clear_confirmed(
        blockchain
    )

    sender_peer = get_request_peer(
        get_peers()
    )

    broadcast_results = broadcast(
        "/receive-block",
        block.to_dict(),
        exclude_peer=sender_peer
    )

    return jsonify({
        "accepted": True,
        "block_index": block.index,
        "block_hash": block.calculate_hash(),
        "broadcast": broadcast_results
    })


# --------------------------------------------------
# Synchronization
# --------------------------------------------------

@app.route(
    "/sync",
    methods=["GET"]
)
def sync():

    results = []

    for peer in get_peers():

        try:

            with urllib.request.urlopen(
                peer + "/blockchain",
                timeout=5
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            candidate = blockchain_from_dict(
                data["blocks"]
            )

            if not candidate.validate():

                results.append({
                    "peer": peer,
                    "accepted": False,
                    "reason": "peer chain invalid"
                })

                continue

            selected = choose_chain(
                candidate,
                blockchain
            )

            if selected is candidate:

                blockchain.chain = (
                    candidate.chain
                )

                mempool.clear_confirmed(
                    blockchain
                )

                results.append({
                    "peer": peer,
                    "accepted": True,
                    "blocks": len(
                        blockchain.chain
                    )
                })

            else:

                results.append({
                    "peer": peer,
                    "accepted": False,
                    "reason": "local chain has equal or greater work"
                })

        except Exception as error:

            results.append({
                "peer": peer,
                "accepted": False,
                "error": str(error)
            })

    return jsonify({
        "node": PORT,
        "blocks": len(
            blockchain.chain
        ),
        "results": results
    })


# --------------------------------------------------
# Application entry point
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "Starting Kyle20000 node on port",
        PORT
    )

    print(
        "Peers:",
        get_peers()
    )

    app.run(
        host="127.0.0.1",
        port=PORT,
        debug=False
    )
