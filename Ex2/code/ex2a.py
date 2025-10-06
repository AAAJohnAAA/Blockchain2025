from sys import exit
from bitcoin.core.script import *
from bitcoin.wallet import CBitcoinSecret
from utils import *
from config import my_private_key, my_public_key, my_address, faucet_address
from ex1 import send_from_P2PKH_transaction


cust1_private_key = CBitcoinSecret(
    'cQLPq7h3ibLbG2QHAKRjgwiz7wWwVPpfCtGMKYTe2DJnHje7AmWH')
cust1_public_key = cust1_private_key.pub
cust2_private_key = CBitcoinSecret(
    'cSUg7LUHzhikgxoDNgY4qLU9sYEwFJbHZefj9KG728nrVARsrXkJ')
cust2_public_key = cust2_private_key.pub
cust3_private_key = CBitcoinSecret(
    'cQZQ9vwjChhF8sHQkaocRw8QR3xStTdtvSsiJDqTAsvMpsXoqa31')
cust3_public_key = cust3_private_key.pub


required_signatures = 3
public_key=[
    cust1_public_key,
    cust2_public_key,
    cust3_public_key
]

ex2a_txout_scriptPubKey = CScript([required_signatures] + public_key + [len(public_key), OP_CHECKMULTISIG])


if __name__ == '__main__':

    amount_to_send = 0.00001
    txid_to_spend = (
        'e709104d5bb4be79214202062d16556915ed1ffda68323daf9b1006056b820a5'
        )
    utxo_index = 0
        

    response = send_from_P2PKH_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        ex2a_txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
