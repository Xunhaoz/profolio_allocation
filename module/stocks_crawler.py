from FinMind.data import DataLoader
import time
import requests
from datetime import date
from dateutil.relativedelta import relativedelta

import global_variable.globals as g


def download_stock(stock_code):
    # login
    api = DataLoader()
    api.login_by_token(api_token=g.GlobalVar.FINDMIND_API_TOKEN)

    # get user limitation
    url = "https://api.web.finmindtrade.com/v2/user_info"
    parload = {"token": g.GlobalVar.FINDMIND_API_TOKEN}
    resp = requests.get(url, params=parload)
    user_count = resp.json()["user_count"]  # 使用次數
    api_request_limit = resp.json()["api_request_limit"]  # api 使用上限

    # wait until unlimited
    time_wait = 0
    while user_count >= api_request_limit - 1:
        time.sleep(3)

    # 設定時間序 十年
    end_date = date.today()
    start_date = end_date - relativedelta(years=10)

    # 取得台股資料
    df = api.taiwan_stock_daily(
        stock_id=stock_code,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    df.set_index('date', drop=True)
    df = df[~(df['close'] == 0)]

    means = df['close'].mean()
    std = df['close'].std()

    df = df[(df['close'] < means + 2 * std)]
    df = df[(df['close'] > means - 2 * std)]

    # save and change index
    path = f"stock_files\\{stock_code}.csv"
    df.to_csv(path)

    return path
