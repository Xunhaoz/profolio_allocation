import sqlite3
import controller.reply_controller as reply_controller


def delete(user_id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (user_id,)
    sql = '''
        DELETE
        FROM user_follow
        WHERE user_id = (?)
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def read(user_id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (user_id,)
    sql = '''
        SELECT *
        FROM user_follow 
        WHERE user_id = (?)
        '''
    result = conn.execute(sql, data).fetchall()

    return result


def delete_connection(user_id, stock_id):
    conn = sqlite3.connect("database/portfolio_management.db")
    data = (user_id, stock_id)
    sql = '''
            DELETE
            FROM user_follow
            WHERE user_id = (?) AND stock_id = (?)
            '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def is_stock(stock_id):
    dic = reply_controller.load_json_file('stock_files/taiwan_stock_info.json')
    if stock_id in dic['taiwan_stock_info']:
        return True
    return False


def read_connection(user_id, stock_id):
    conn = sqlite3.connect("database/portfolio_management.db")
    data = (user_id, stock_id)
    sql = '''
            SELECT *
            FROM user_follow
            WHERE user_id = (?) AND stock_id = (?)
            '''
    result = conn.execute(sql, data).fetchone()
    conn.close()
    return result


def create_connection(user_id, stock_id):
    conn = sqlite3.connect("database/portfolio_management.db")
    data = (user_id, stock_id)
    sql = """INSERT
        INTO user_follow(user_id, stock_id)
        VALUES(?, ?)"""
    conn.execute(sql, data)
    conn.commit()
    conn.close()
    return None
