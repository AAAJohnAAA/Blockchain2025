from sys import exit
from bitcoin.core.script import *

from utils import *
from config import my_private_key, my_public_key, my_address, faucet_address
from ex1 import send_from_P2PKH_transaction

ex3a_txout_scriptPubKey = [
    OP_2DUP,
    OP_ADD,
    320803200,
    OP_EQUALVERIFY,
    OP_SUB,
    502160016,
    OP_EQUAL
]

def btc_to_sats(btc):
    return int(round(btc * 100_000_000))

def sats_to_btc(sats):
    return sats / 100_000_000.0

if __name__ == '__main__':
    txid_to_spend = '9cf2734705e32cb7fbd4ec2e0e0b3e66a7b593c98510cc0e7c6d5ef00a75f121'
    utxo_index = 1
    utxo_btc = 0.00154493
    utxo_sats = btc_to_sats(utxo_btc) 
    desired_amount_btc = 0.00001
    desired_amount_sats = btc_to_sats(desired_amount_btc)
    fee_rate_sat_per_vB = 100  
    estimated_vsize = 200  
    estimated_fee_sats = fee_rate_sat_per_vB * estimated_vsize 
    DUST_LIMIT_SATS = 546 

    print("UTXO 总额: {} sats".format(utxo_sats))
    print("期望发送到脚本: {} sats".format(desired_amount_sats))
    print("估算费率: {} sat/vB, 估算vsize: {} vB -> 估算手续费: {} sats".format(
        fee_rate_sat_per_vB, estimated_vsize, estimated_fee_sats))

    change_sats = utxo_sats - desired_amount_sats - estimated_fee_sats

    if change_sats <= DUST_LIMIT_SATS:
        adjusted_fee_sats = utxo_sats - desired_amount_sats
        print("计算到找零 <= dust（{} sats），不生成找零输出。".format(DUST_LIMIT_SATS))
        print("把剩余并入手续费 -> 实际手续费: {} sats".format(adjusted_fee_sats))
        amount_to_send_btc = sats_to_btc(desired_amount_sats)
        actual_fee_sats = adjusted_fee_sats
        change_btc = 0.0
    else:
        print("预计会生成找零: {} sats (返回到 my_address)".format(change_sats))
        amount_to_send_btc = sats_to_btc(desired_amount_sats)
        actual_fee_sats = estimated_fee_sats
        change_btc = sats_to_btc(change_sats)

    print("最终决定 -> 发送到脚本: {} sats ({} BTC)".format(
        desired_amount_sats, amount_to_send_btc))
    print("最终矿工费 (sats): {}".format(actual_fee_sats))
    if change_btc > 0:
        print("找零 (sats): {} ({} BTC) 将返回到 {}".format(change_sats, change_btc, my_address))
    else:
        print("没有单独的找零输出（找零并入手续费）。")
    try:
        response = send_from_P2PKH_transaction(
            amount_to_send_btc,
            txid_to_spend,
            utxo_index,
            ex3a_txout_scriptPubKey,
            fee=actual_fee_sats,          
            change_address=my_address,   
            change_amount=change_btc     
        )
    except TypeError:
        print("send_from_P2PKH_transaction 不接受 fee/change_address 参数，使用回退策略：")
        fallback_amount_sats = utxo_sats - actual_fee_sats
        if fallback_amount_sats <= 0:
            raise SystemExit("回退后输出金额 <= 0，无法构造交易，请降低 fee_rate 或增加 UTXO 额度。")
        fallback_amount_btc = sats_to_btc(fallback_amount_sats)
        print("回退后将发送到脚本 (sats): {}, (BTC): {}".format(fallback_amount_sats, fallback_amount_btc))
        response = send_from_P2PKH_transaction(
            fallback_amount_btc,
            txid_to_spend,
            utxo_index,
            ex3a_txout_scriptPubKey
        )
    try:
        print(response.status_code, response.reason)
        print(response.text)
    except Exception:
        print("send_from_P2PKH_transaction 返回: {}".format(response))
