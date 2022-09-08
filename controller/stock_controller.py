import sqlite3
import module.stocks_crawler as stocks_crawler
import module.feature_calculator as feature_calculator


def create(stock_code):
    if read_by_stock_code(stock_code):
        return

    # call cal function gain (stock_code, mean, variance, skewness, kurt)
    path = stocks_crawler.download_stock(stock_code)
    mean = feature_calculator.cal_mean(path)
    variance = feature_calculator.cal_variance(path)
    skewness, kurt = feature_calculator.cal_skew_kurt(path)

    conn = sqlite3.connect('database/portfolio_management.db')
    data = (stock_code, mean, variance, skewness, kurt)
    sql = "INSERT INTO stock \
        (stock_code, mean, variance, skewness, kurt) VALUES \
        (?, ?, ?, ?, ?)"
    conn.execute(sql, data)
    conn.commit()
    conn.close()


#
#
# def delete(id):
#     conn = sqlite3.connect(os.path.join(globals.BASE_PATH, 'database', 'portfolio_management.db'))
#     data = (id,)
#     sql = '''
#         DELETE
#         FROM stock
#         WHERE id = (?)
#         '''
#     conn.execute(sql, data)
#     conn.commit()
#     conn.close()

def read_by_stock_code(stock_code):
    conn = sqlite3.connect('database/portfolio_management.db')
    sql = "SELECT * FROM stock WHERE stock_code = (?)"
    stock = conn.execute(sql, (stock_code,))
    stock = stock.fetchone()
    conn.close()
    return stock[0] if stock else None


def read_by_stock_id(stock_id):
    conn = sqlite3.connect('database/portfolio_management.db')
    sql = "SELECT * FROM stock WHERE id = (?)"
    stock = conn.execute(sql, (stock_id,))
    stock = stock.fetchone()
    conn.close()
    return stock[1]
#
#
# def read_by_stock_id(stock_id):
#     conn = sqlite3.connect(os.path.join(globals.BASE_PATH, 'database', 'portfolio_management.db'))
#     sql = "SELECT * FROM stock WHERE id = (?)"
#     stock = conn.execute(sql, (stock_id,))
#     stock = stock.fetchall()
#     conn.close()
#     # print(stock if stock == None else stock[0])
#     return stock if stock is None else stock
#
#
# if __name__ == '__main__':
#     read_by_stock_code("2335")
