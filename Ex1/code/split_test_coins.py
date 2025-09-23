from bitcoin.core.script import *

from code.utils import *
from code.config import (my_private_key, my_public_key, my_address,
                    faucet_address)

#分币操作
def split_coins(amount_to_send, txid_to_spend, utxo_index, n):
    txin_scriptPubKey = my_address.to_scriptPubKey()
    txin = create_txin(txid_to_spend, utxo_index)
    txout_scriptPubKey = my_address.to_scriptPubKey()
    txout = create_txout(amount_to_send / n, txout_scriptPubKey)
    tx = CMutableTransaction([txin], [txout]*n)
    sighash = SignatureHash(txin_scriptPubKey, tx,
                            0, SIGHASH_ALL)
    txin.scriptSig = CScript([my_private_key.sign(sighash) + bytes([SIGHASH_ALL]),
                              my_public_key])
    VerifyScript(txin.scriptSig, txin_scriptPubKey,
                 tx, 0, (SCRIPT_VERIFY_P2SH,))
    response = broadcast_transaction(tx)
    print(response.status_code, response.reason)
    print(response.text)

if __name__ == '__main__':

    amount_to_send = 0.0001
    txid_to_spend = (
        'b8a50f1883a4c5b05a1334a7c3e23130953afe5d8b41f9c32343ac9ec69900ea')
    utxo_index = 0
    n=10
    split_coins(amount_to_send, txid_to_spend, utxo_index, n)
