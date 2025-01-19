import pandas as pd
import sys
sys.path.append('../')
import common
from common import const,utils
import numpy as np

""" 
以下の購入方法での払い戻し金額を計算する関数を格納するモジュール
- 単勝,複勝,枠連,馬連,ワイド,馬単,三連複,三連単
"""


def calculate_return_tansho(refund_data, race_id, amount, purchase_horse_number):
    """
    単勝の払い戻し金額を計算する関数

    Parameters:
        refund_data (DataFrame): 払い戻しデータが格納されたDataFrame
        race_id (int): レースID
        amount (int): 購入金額
        purchase_horse_number (int): 購入した馬の馬番号

    Returns:
        int: 払い戻し金額
    """
    hit_result = refund_data[(refund_data['レースID'] == race_id) & (refund_data['種別'] == '単勝')]
    if  hit_result[hit_result['当選番号']==str(purchase_horse_number)].size > 0:
        odds = utils.string2int(hit_result['金額'].values[0]) / 100
    else:
        odds = 0
    return amount * odds


def calculate_return_hukusho(refund_data, race_id, amount, purchase_horse_number):
    """
    指定されたレースIDと馬番に対応する払い戻し金額を計算する関数

    Parameters:
    refund_data (DataFrame): 複勝の払い戻しデータを含むDataFrame
    race_id (int): レースID
    amount (int): 購入金額
    purchase_horse_number (int): 購入馬番

    Returns:
    int: 計算された払い戻し金額
    """
    hit_result = refund_data[(refund_data['レースID'] == race_id) & (refund_data['種別'] == '複勝')]

    hit_horse_numbers = hit_result['当選番号'].values[0].split(' ')
    hit_odds = hit_result['金額'].values[0].split(' ')

    try:
        index = hit_horse_numbers.index(str(purchase_horse_number))
        odds = utils.string2int(hit_odds[index]) / 100
    except ValueError:
        odds = 0

    return amount * odds



def calculate_return_wakuren(refund_data, race_id, amount, purchase_waku_numbers):
    """
    枠連の払い戻し金額を計算する関数

    Parameters:
        refund_data (DataFrame): 払い戻しデータのDataFrame
        race_id (int): レースID
        amount (int): 購入金額
        purchase_waku_numbers (list): 購入した枠番号のリスト

    Returns:
        int: 払い戻し金額
    """
    hit_result = refund_data[(refund_data['レースID'] == race_id) & (refund_data['種別'] == '枠連')]

    hit_waku_numbers = list(
        map(lambda x: int(x),
            filter(lambda x: utils.is_int(x),
                   hit_result['当選番号'].values[0].split(' '))))

    if set(hit_waku_numbers) == set(purchase_waku_numbers):
        odds = utils.string2int(hit_result['金額'].values[0]) / 100
    else:
        odds = 0


    return amount * odds


def calculate_return_umaren(refund_data, race_id, amount, purchase_horse_numbers):
    """
    馬連の払い戻し金額を計算する関数

    Parameters:
        refund_data (DataFrame): 払い戻しデータのDataFrame
        race_id (int): レースID
        amount (int): 購入金額
        purchase_horse_numbers (list): 購入した馬番号のリスト

    Returns:
        int: 払い戻し金額
    """
    hit_result = refund_data[(refund_data['レースID'] == race_id) & (refund_data['種別'] == '馬連')]

    hit_horse_numbers = list(
        map(lambda x: int(x),
            filter(lambda x: utils.is_int(x),
                   hit_result['当選番号'].values[0].split(' '))))
    hit_odds = utils.string2int(hit_result['金額'].values[0])

    if set(hit_horse_numbers) == set(purchase_horse_numbers):
        odds = hit_odds / 100
    else:
        odds = 0


    return amount * odds


def calculate_return_wide(refund_data, race_id, amount, purchase_horse_numbers):
    """
    ワイドの払い戻し金額を計算する関数

    Parameters:
        refund_data (DataFrame): 払い戻しデータのDataFrame
        race_id (int): レースID
        amount (int): 購入金額
        purchase_horse_numbers (list): 購入した馬番号のリスト。　例）[1, 2]

    Returns:
        int: 払い戻し金額
    """
    hit_result = refund_data[(refund_data['レースID'] == race_id) & (refund_data['種別'] == 'ワイド')]

    hit_horse_numbers_list = np.array_split(list(
        map(lambda x: int(x),
            filter(lambda x: utils.is_int(x),
                   hit_result['当選番号'].values[0].split(' ')))),3)
    hit_odds = hit_result['金額'].values[0].split(' ')

    i = 0
    odds = 0

    for hit_horse_numbers in hit_horse_numbers_list:
        if set(purchase_horse_numbers) == set(hit_horse_numbers):
            odds = utils.string2int(hit_odds[i]) / 100
            break
        i += 1

    return amount * odds



def calculate_return_umatan(refund_data, race_id, amount, purchase_horse_numbers):
    """
    馬単の払い戻し金額を計算する関数

    Parameters:
        refund_data (DataFrame): 払い戻しデータのDataFrame
        race_id (int): レースID
        amount (int): 購入金額
        purchase_horse_numbers (list): 購入した馬番号のリスト

    Returns:
        int: 払い戻し金額
    """
    hit_result = refund_data[(refund_data['レースID'] == race_id) & (refund_data['種別'] == '馬単')]

    hit_horse_numbers = list(
        map(lambda x: int(x),
            filter(lambda x: utils.is_int(x),
                   hit_result['当選番号'].values[0].split(' '))))
    hit_odds = utils.string2int(hit_result['金額'].values[0])

    if hit_horse_numbers == purchase_horse_numbers:
        odds = hit_odds / 100
    else:
        odds = 0

    return amount * odds



def calculate_return_3renpuku(refund_data, race_id, amount, purchase_horse_numbers):
    """
    三連複の払い戻し金額を計算する関数

    Parameters:
        refund_data (DataFrame): 払い戻しデータのDataFrame
        race_id (int): レースID
        amount (int): 購入金額
        purchase_horse_numbers (list): 購入した馬番号のリスト。3つの馬番号を格納している

    Returns:
        int: 払い戻し金額
    """
    hit_result = refund_data[(refund_data['レースID'] == race_id) & (refund_data['種別'] == '三連複')]

    hit_horse_numbers = list(
        map(lambda x: int(x),
            filter(lambda x: utils.is_int(x),
                   hit_result['当選番号'].values[0].split(' '))))

    # 同着の場合は複数の払い戻しがあるためその考慮
    if len(hit_horse_numbers) != 3:
        i=0
        for _hit_horse_numbers in np.array_split(hit_horse_numbers,2):
            if set(purchase_horse_numbers) == set(_hit_horse_numbers):
                odds = utils.string2int(hit_result['金額'].values[0].split(' ')[i])/ 100
                break
            else:
                odds = 0
    else:
        if set(purchase_horse_numbers) == set(hit_horse_numbers):
            odds = utils.string2int(hit_result['金額'].values[0])/ 100
        else:
            odds = 0

    return amount * odds



def calculate_return_3rentan(refund_data, race_id, amount, purchase_horse_numbers):
    """
    三連単の払い戻し金額を計算する関数

    Parameters:
        refund_data (DataFrame): 払い戻しデータのDataFrame
        race_id (int): レースID
        amount (int): 購入金額
        purchase_horse_numbers (list): 購入した馬番号のリスト。3つの馬番号を格納している

    Returns:
        int: 払い戻し金額
    """
    hit_result = refund_data[(refund_data['レースID'] == race_id) & (refund_data['種別'] == '三連単')]

    hit_horse_numbers = list(
        map(lambda x: int(x),
            filter(lambda x: utils.is_int(x),
                   hit_result['当選番号'].values[0].split(' '))))


    # 同着の場合は複数の払い戻しがあるためその考慮
    if len(hit_horse_numbers) != 3:
        i=0
        for _hit_horse_numbers in np.array_split(hit_horse_numbers,2):
            if purchase_horse_numbers == list(_hit_horse_numbers):
                odds = utils.string2int(hit_result['金額'].values[0].split(' ')[i])/ 100
                break
            else:
                odds = 0
    else:
        if purchase_horse_numbers == hit_horse_numbers:
            odds = utils.string2int(hit_result['金額'].values[0])/ 100

        else:
            odds = 0
    return amount * odds
