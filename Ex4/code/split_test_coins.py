from bitcoin import SelectParams
from bitcoin.core import CMutableTransaction, x
from bitcoin.core.script import CScript, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH

from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress


from utils import create_txin, create_txout, broadcast_transaction


def split_coins(amount_to_send, txid_to_spend, utxo_index, n, network):
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
    response = broadcast_transaction(tx, network)
    print(response.status_code, response.reason)
    print(response.text)

if __name__ == '__main__':
    SelectParams('testnet')

    ######################################################################
    # TODO: set these parameters correctly
    #

    hex_private_key = '83b0324811c37e1d9a4d0d3c322123a15b347d7ac885f42aa2e3ede2306c63a2'

# 将十六进制私钥转换为字节
    private_key_bytes = bytes.fromhex(hex_private_key)

# 创建 CBitcoinSecret 
    my_private_key = CBitcoinSecret.from_secret_bytes(private_key_bytes)

    my_public_key = my_private_key.pub
    my_address = P2PKHBitcoinAddress.from_pubkey(my_public_key)

    amount_to_send = 0.01 # amount of BTC in the output you're splitting minus fee
    txid_to_spend = (
        '6e09330daba0641c4ba32f2d3f06e7654a10a7af5363bf9bd2e73b1b959ae96a')
    utxo_index = 0
    n = 10 # number of outputs to split the input into
    network = 'bcy-test' # either 'btc-test3' or 'bcy-test'

    #
    #
    ######################################################################

    split_coins(amount_to_send, txid_to_spend, utxo_index, n, network)