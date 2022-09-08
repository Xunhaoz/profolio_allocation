import json
import sqlite3
import time


def delete(user_id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (user_id,)
    sql = '''
        DELETE
        FROM alloc_result
        WHERE user_id = (?)
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def read_update_time(user_id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (user_id,)
    sql = '''
            SELECT update_time 
            FROM alloc_result
            WHERE user_id = (?)
            '''
    update_time = conn.execute(sql, data).fetchone()
    conn.close()
    return update_time[0] if update_time else 0


def set_efficient_frontier(user_id, result_dict):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (json.dumps(result_dict, indent=4), user_id)
    sql = '''
        UPDATE alloc_result SET efficient_frontier=(?) WHERE user_id=(?);
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def create(user_id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (user_id, time.time())
    sql = '''
                INSERT INTO alloc_result (user_id, update_time)
                VALUES (?, ?)
                '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def update_update_time(user_id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (time.time(), user_id)
    sql = '''
                UPDATE alloc_result
                SET update_time = (?) 
                WHERE user_id = (?)
                '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def set_risk_party(user_id, result_dict):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (json.dumps(result_dict, indent=4), user_id)
    sql = '''
        UPDATE alloc_result SET risky_party=(?) WHERE user_id=(?);
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def set_black_litterman(user_id, result_dict):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (json.dumps(result_dict, indent=4), user_id)
    sql = '''
        UPDATE alloc_result SET black_litterman=(?) WHERE user_id=(?);
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def read_allocate_result(user_id, model):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (user_id,)
    sql = '''
        SELECT * FROM alloc_result WHERE user_id = (?)
        '''
    result = conn.execute(sql, data).fetchone()
    conn.close()
    return result[model + 1]
