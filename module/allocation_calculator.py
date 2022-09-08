# System import
import os
import pprint as pp
import json
import argparse
import logging
import controller.user_follow_controller as user_follow_controller
import controller.stock_controller as stock_controller
# Twisted import
import numpy as np
import pandas as pd
from argparse import RawTextHelpFormatter
from tqdm import tqdm
import pypfopt
from pypfopt import expected_returns, risk_models
import yfinance as yf
import controller.user_controller as user_controller
import controller.alloc_result_controller as alloc_result_controller
import sqlite3

'''
This is a scrip which can help calculating better assets allocation from stocks history data. 
'''


class StockClass:
    """
        this is a stock class to read stocks individually.

        Inputs:
            dir_path: string
            csv_name: string

        Public methods:
            get_stock_name(): return string
            get_stock_dataframe(): return dataframe
            get_stock_period(): return dict{stock_data_len:int, start_time:str, end_time:str}
            get_stock_pct_change(mean: bool):   if mean is true, return mean_pct_change: int
                                                else return a dataframe
                                                !important in order to count pct_change we will lose the fist data
                                                so the length of return dataframe will minus one
            get_stock_performance(): return dict{expect_return:float, sharpe_ratio:float}
            get_all_stock_info(): return all above in a dic
    """

    def __init__(self, dir_path, csv_name):
        self.stock_dataframe = pd.read_csv(os.path.join(dir_path, csv_name) + '.csv')
        self.stock_name = csv_name
        self.stock_data_len = len(self.stock_dataframe)
        self.pct_change = self.stock_dataframe['close'].pct_change().dropna()

    def get_stock_name(self):
        return self.stock_name

    def get_stock_dataframe(self):
        return self.stock_dataframe

    def get_stock_period(self):
        start_time = self.stock_dataframe['date'][0]
        end_time = self.stock_dataframe['date'][self.stock_data_len - 1]
        return {'stock_data_len': self.stock_data_len, 'start_time': start_time, 'end_time': end_time}

    # drop na would make the length minus one
    def get_stock_pct_change(self, mean=False):
        return self.pct_change.dropna().mean() if mean else self.pct_change.dropna()

    def get_stock_performance(self):
        expect_return = self.pct_change.mean() * 252
        sharpe_ratio = expect_return / (self.pct_change.std() * (252 ** 0.5))
        return {'expect_return': expect_return, 'sharpe_ratio': sharpe_ratio}

    def get_all_stock_info(self):
        info = {}
        info['name'] = self.stock_name
        info['mean_pct_change'] = self.get_stock_pct_change(mean=True)
        info['period'] = self.get_stock_period()
        info['performance'] = self.get_stock_performance()
        return info


def data_pre_treatment(stocks_class_list):
    """
    資料預處理
    將原本個別以tickit為欄的dataframe取出收盤價
    在彙整到以只有個股收盤價的單一dataframe中
    """
    concat_list = []
    for stock in stocks_class_list:  # 取得個股收盤價加入串列
        stock_df = stock.get_stock_dataframe()[['close', 'date']]
        stock_df = stock_df.rename(columns={'close': stock.get_stock_name()})
        stock_df = stock_df.set_index('date')
        concat_list.append(stock_df)

    data_for_pypfopt = concat_list[0]
    for stock in concat_list[1:]:
        data_for_pypfopt = data_for_pypfopt.merge(stock, how='inner', left_index=True, right_index=True)

    return data_for_pypfopt


def check_stock_info(stock_class_list, stock_name, save):
    """查看各股票name, mean_pct_change, period, and performance"""
    result_dict = {}
    if stock_name == 'all':
        for index, stock in enumerate(stock_class_list):
            result_dict[index] = stock.get_all_stock_info()
    else:
        for stock in stock_class_list:
            if stock.get_stock_name() == stock_name:
                result_dict = stock.get_all_stock_info()
    if save:
        with open('result.json', 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)
    else:
        pp.pprint(result_dict)
    return result_dict


def save_result(weights, clean_weight, portfolio_performance, save):
    """
        輸入weights, clean_weight, portfolio_performance, and save
        若 save為 True將儲存成.json檔 否則印在終端機上
    """
    result_dict = {'weights': weights, 'clean_weight': clean_weight, 'performance': {}}
    result_dict['performance']['expected_annual_return'] = portfolio_performance[0]
    result_dict['performance']['annual_volatility'] = portfolio_performance[1]
    result_dict['performance']['sharpe_ratio'] = portfolio_performance[2]
    if save:
        with open('result.json', 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)

    return result_dict


def check_boundary_exist(stock_boundary_path, stock_class_list):
    """
    檢查個別資產比例邊界檔是否存在
    存在則讀取 否則產生個別資產比例邊界檔並回傳None
    """
    if not os.path.exists(stock_boundary_path):
        stock_name_dict = {}
        for stock in stock_class_list:
            stock_name_dict[stock.stock_name] = {}
            stock_name_dict[stock.stock_name]['upper_bound'] = 0.0
            stock_name_dict[stock.stock_name]['lower_bound'] = 0.0
        with open(stock_boundary_path, 'w', encoding='utf-8') as f:
            json.dump(stock_name_dict, f, ensure_ascii=False, indent=4)
        logging.error('boundary.json doesn\'t exits')
        return
    else:
        with open(stock_boundary_path, 'r') as f:
            boundary_dict = json.load(f)

    upper_bound_array = []
    lower_bound_array = []
    has_return = False
    for stock in boundary_dict:
        has_return = True
        upper_bound_array.append(boundary_dict[stock]['upper_bound'])
        lower_bound_array.append(boundary_dict[stock]['lower_bound'])
    return upper_bound_array, lower_bound_array, has_return


def exec_general_efficient_frontier(expected_returns, covariance_matrix, weight_bounds, target_return, market_neutral,
                                    risk_free_rate):
    """計算效率前緣 並回傳結果"""
    # 計算效率前緣
    ef = pypfopt.efficient_frontier.EfficientFrontier(expected_returns, covariance_matrix, weight_bounds=weight_bounds)

    # 檢查是否有目標回報
    if target_return:
        # 以目標報酬率及市場情況計算資產配比重
        weights = ef.efficient_return(target_return=target_return, market_neutral=market_neutral)
    else:
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)  # 以最大夏普比例計算資產配比重

    result_dict = save_result(weights, ef.clean_weights(), ef.portfolio_performance(risk_free_rate=risk_free_rate),
                              False)
    return result_dict


def exec_black_litterman(stock_class_list, stocks_df, covariance_matrix,
                         weight_bounds, target_return, market_neutral, risk_free_rate):
    """將 views, prior套用，預測期望報酬，再計算資產配置權重"""
    try:
        with open('module/view.json', 'r') as f:
            view_dict_all = json.load(f)
    except EOFError:
        view_dict_all = {}

    try:
        with open('module/mcap.json', 'r') as f:
            mcap_all = json.load(f)
    except EOFError:
        mcap_all = {}

    # 取得股票總市值
    mcaps = {}
    view_dict = {}
    for stock in tqdm(stock_class_list):
        mcaps[stock.get_stock_name()] = mcap_all[stock.get_stock_name()] if stock.get_stock_name() in mcap_all else None
        view_dict[stock.get_stock_name()] = view_dict_all[stock.get_stock_name()]

    # 在市值中計算取得市場對於回報的估計
    delta = pypfopt.black_litterman.market_implied_risk_aversion(stocks_df)
    prior = pypfopt.black_litterman.market_implied_prior_returns(mcaps, delta, covariance_matrix)

    # 套入模型計算估計報酬
    bl = pypfopt.BlackLittermanModel(covariance_matrix, pi=prior, absolute_views=view_dict, prior=prior)
    rets = bl.bl_returns()
    ef = pypfopt.efficient_frontier.EfficientFrontier(rets, covariance_matrix, weight_bounds=weight_bounds)

    if target_return:
        weights = ef.efficient_return(target_return=target_return, market_neutral=market_neutral)
    else:
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
    result_dict = save_result(weights, ef.clean_weights(), ef.portfolio_performance(), 'False')
    return result_dict


def exec_hierarchical_risky_party(stocks_df, covariance_matrix, risk_free_rate, frequency):
    """將每日pct_change, covariance_matrix, and 交易頻率 套入 Hierarchical Risk Parity計算解果"""
    returns = stocks_df.pct_change().dropna()
    HRP = pypfopt.hierarchical_portfolio.HRPOpt(returns=returns, cov_matrix=covariance_matrix)
    result_dict = save_result(HRP.optimize(), HRP.clean_weights(),
                              HRP.portfolio_performance(risk_free_rate=risk_free_rate, frequency=frequency), False)

    return result_dict


def allocation_cal(user_id):
    args = {}
    if user_controller.read_args(user_id):
        args = json.loads(user_controller.read_args(user_id))
        args['weight_bounds'] = (args['lower_bound'], args['upper_bound'])
    else:
        args['weight_bounds'] = (0, 1)
        args['target_return'] = 0.0
        args['market_neutral'] = False
        args['risk_free_rate'] = user_controller.read_risk_free_rate(user_id)

    stocks = user_follow_controller.read(user_id)
    stock_class_list = []

    for stock in stocks:
        stock = stock_controller.read_by_stock_id(stock[2])
        stock_class_list.append(StockClass('stock_files', stock))

    stock_df = data_pre_treatment(stock_class_list)

    mu = expected_returns.mean_historical_return(stock_df)
    S = risk_models.CovarianceShrinkage(stock_df).ledoit_wolf()

    efficient_frontier = exec_general_efficient_frontier(mu, S, args['weight_bounds'], args['target_return'],
                                                         args['market_neutral'], args['risk_free_rate'])
    alloc_result_controller.set_efficient_frontier(user_id, efficient_frontier)

    # black_litterman = exec_black_litterman(stock_class_list, stock_df, S, args['weight_bounds'],
    #                                        args['target_return'], args['market_neutral'], args['risk_free_rate'])
    # alloc_result_controller.set_risk_party(user_id, black_litterman)

    risky_party = exec_hierarchical_risky_party(stock_df, S, args['risk_free_rate'], 252)
    alloc_result_controller.set_risk_party(user_id, risky_party)

    alloc_result_controller.update_update_time(user_id)
