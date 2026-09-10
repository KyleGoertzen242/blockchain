from node.wallet import Wallet


wallet = Wallet()

print("Kyle20000 Wallet")
print("----------------")

print("Address:")
print(wallet.address)

print("\nPublic key:")
print(wallet.public_key)

message = "Hello Kyle20000"

signature = wallet.sign(message)

print("\nSignature:")
print(signature)

valid = Wallet.verify(
    wallet.public_key,
    message,
    signature
)

print("\nSignature valid:", valid)