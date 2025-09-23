from bitcoin.core.script import *
from code.utils import *
from code.config import (
    my_private_key, my_public_key, my_address, faucet_address
)

def create_P2PKH_scriptPubKey(address):
    script = address.to_scriptPubKey()
    pubkey_hash = script[3:-2]
    return [
        OP_DUP,
        OP_HASH160,
        pubkey_hash,
        OP_EQUALVERIFY,
        OP_CHECKSIG
    ]

def create_P2PKH_scriptSig(txin, txout, script_pubkey):
    signature = create_OP_CHECKSIG_signature(
        txin, txout, script_pubkey, my_private_key
    )
    return [signature, my_public_key]

def build_P2PKH_transaction(amount, txid, utxo_index, recipient_scriptPubKey):
    txout = create_txout(amount, recipient_scriptPubKey)
    sender_scriptPubKey = create_P2PKH_scriptPubKey(my_address)
    txin = create_txin(txid, utxo_index)
    txin_scriptSig = create_P2PKH_scriptSig(txin, txout, sender_scriptPubKey)

    signed_tx = create_signed_transaction(
        txin, txout, sender_scriptPubKey, txin_scriptSig
    )
    return signed_tx

def send_transaction(amount, txid, utxo_index, recipient_address):
    recipient_scriptPubKey = create_P2PKH_scriptPubKey(recipient_address)
    tx = build_P2PKH_transaction(amount, txid, utxo_index, recipient_scriptPubKey)
    return broadcast_transaction(tx)

if __name__ == '__main__':
    amount = 0.00001
    txid = 'e709104d5bb4be79214202062d16556915ed1ffda68323daf9b1006056b820a5'
    utxo_index = 0

    response = send_transaction(amount, txid, utxo_index, faucet_address)

    print(response.status_code, response.reason)
    print(response.text)
