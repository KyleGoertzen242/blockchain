# blockchain
blockchain


Copyright Kyle Rodney David Goertzen

download blockchain-main.zip

download python3

download pip

install: python3 -m pip install Flask
install: python3 -m pip install flask_cors
install: python3 -m pip install PyNaCl

unzip blockchain-main.zip

navigate with cd to blockchain-main>kyle20000>

run: blockchain-main>kyle20000>python3 -c "from node.wallet import Wallet; w=Wallet(); print('Address:', w.address); print('Public Key:', w.public_key); print('Private Key:', w.private_key)"

store your private key safely

run: blockchain-main>kyle20000>python3 -m node.server 5001

now you can mine on a local server and your balance will persist even if it goes offline!
