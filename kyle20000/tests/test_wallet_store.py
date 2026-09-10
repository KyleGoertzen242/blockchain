from node.wallet import Wallet
from node.wallet_store import save_wallet, load_wallet


def main():
    wallet = Wallet()

    save_wallet(wallet)

    loaded = load_wallet()

    print(
        "Wallet loaded:",
        loaded is not None
    )

    print(
        "Address matches:",
        loaded["address"] == wallet.address
    )

    print(
        "Public key matches:",
        loaded["public_key"] == wallet.public_key
    )

    print(
        "Private key exists:",
        bool(loaded["private_key"])
    )


if __name__ == "__main__":
    main()