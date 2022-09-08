import sqlite3

"""
這是一個無關專案的獨立資料庫建立腳本，絕大多數時間為獨立運行
因此在腳本中的路徑是以此腳本為出發點的相對路徑
非全局之相對路徑
全局之相對路徑請以 app.py 出發
"""

if __name__ == "__main__":
    create_db_common = [

        "CREATE TABLE user(\
            id integer primary key autoincrement, \
            line_id text, \
            risk_free_rate real, \
            model_type integer, \
            args text, \
            create_time timestamp, \
            update_time timestamp\
        )",

        "CREATE TABLE stock( \
            id integer primary key autoincrement, \
            stock_code text, \
            mean real, \
            variance real, \
            skewness real, \
            kurt real \
        )",

        "CREATE TABLE model( \
            id integer primary key, \
            name text \
        )",

        "CREATE TABLE sheet_ans( \
            user_id INTEGER \
            primary key, \
            Q1 INTEGER, \
            Q2 INTEGER, \
            Q3 INTEGER, \
            Q4 INTEGER, \
            Q5 INTEGER, \
            Q6 INTEGER, \
            Q7 INTEGER, \
            Q8 INTEGER, \
            Q9 INTEGER \
        )",

        "CREATE TABLE alloc_result( \
            user_id integer primary key, \
            efficient_frontier text, \
            black_litterman text, \
            risky_party text, \
            update_time timestamp \
        )",

        "CREATE TABLE user_follow( \
            id integer primary key autoincrement, \
            user_id integer, \
            stock_id integer \
        )"
    ]

    add_model_common = "INSERT INTO model \
                        (id, name) \
                        VALUES (?, ?)"

    models = ['efficient frontier', 'black litterman', 'risky party']

    conn = sqlite3.connect('portfolio_management.db')
    for sql_common in create_db_common:
        conn.execute(sql_common)
        conn.commit()

    for k, model in enumerate(models):
        conn.execute(add_model_common, (k, model))
        conn.commit()

    conn.close()
