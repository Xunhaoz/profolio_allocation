import pandas as pd


def cal_max_drawdown(stock_path):
    df = pd.read_csv(stock_path)
    max_price = df['close'].max(axis=0, skipna=True)
    min_price = df['close'].min(axis=0, skipna=True)
    max_drawdown = (min_price - max_price) / max_price
    return max_price, min_price, max_drawdown


def cal_irr(stock_path):
    df = pd.read_csv(stock_path)['close']
    dr = df.pct_change().dropna()  # 取得損益百分比
    pr = dr.prod() ** (1 / len(dr))  # 幾何平均數
    irr = pr ** 252
    return irr


def cal_volatility(stock_path):
    df = pd.read_csv(stock_path)['close']
    dr = df.pct_change().dropna()
    volatility = dr.std() * (252 ** 0.5)  # 年畫波動度
    return volatility


def cal_skew_kurt(stock_path):
    df = pd.read_csv(stock_path)['close']
    dr = df.pct_change().dropna()
    skewness = dr.skew()
    kurt = dr.kurt()
    return skewness, kurt


def cal_sortino_ratio(stock_path):
    df = pd.read_csv(stock_path)['close']
    dr = df.pct_change().dropna()
    mean = dr.mean() * 252
    std_neg = dr[dr < 0].std() * (252 ** 0.5)
    sortino_ratio = mean / std_neg
    return sortino_ratio


def cal_mean(stock_path):
    df = pd.read_csv(stock_path)['close']
    df = df.pct_change().dropna()
    return df.mean()


def cal_variance(stock_path):
    df = pd.read_csv(stock_path)['close']
    df = df.pct_change().dropna()
    return df.var()
