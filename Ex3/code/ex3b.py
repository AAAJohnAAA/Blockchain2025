from sys import exit
from bitcoin.core.script import *

from utils import *
from config import my_private_key, my_public_key, my_address, faucet_address
from ex1 import P2PKH_scriptPubKey
from ex3a import ex3a_txout_scriptPubKey

amount_to_send = 0.000005
txid_to_spend = 'ce1f1f8a8764d0f5a9ea3f6544240106239738d76968945d3addac81dac3ad74'
utxo_index = 0

txin_scriptPubKey = ex3a_txout_scriptPubKey

txin_scriptSig = [411481608,-90678408]

txout_scriptPubKey = P2PKH_scriptPubKey(faucet_address)

response = send_from_custom_transaction(
    amount_to_send, txid_to_spend, utxo_index,
    txin_scriptPubKey, txin_scriptSig, txout_scriptPubKey)
print(response.status_code, response.reason)
print(response.text)
