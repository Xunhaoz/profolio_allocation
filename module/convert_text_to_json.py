def set_risk_bound(text):
    result = {}
    for line in text.split('\n'):
        if "無風險資產比例： " in line:
            try:
                result['risk_free_rate'] = float(line.replace("無風險資產比例： ", ""))
            except ValueError:
                result["target_return"] = 0.02

        elif "市場中立策略： " in line:
            result['market_neutral'] = True if "是" in line else False

        elif "預期報酬： " in line:
            try:
                result['target_return'] = float(line.replace("預期報酬： ", ""))
            except ValueError:
                result["target_return"] = 1.0

        elif "投資組合比例上界： " in line:
            try:
                result["upper_bound"] = float(line.replace("投資組合比例上界： ", ""))
            except ValueError:
                result["upper_bound"] = 1.0

        elif "投資組合比例下界： " in line:
            try:
                result["lower_bound"] = float(line.replace("投資組合比例下界： ", ""))
            except ValueError:
                result["lower_bound"] = 0.0
    return result
