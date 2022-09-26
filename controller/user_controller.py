import sqlite3
import time
import json
import os


def create(line_id):
    conn = sqlite3.connect("database/portfolio_management.db")
    data = (line_id, time.time(), 0)
    sql = '''
        INSERT
        INTO user(line_id, create_time, model_type)
        VALUES(?, ?, ?)
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def delete(user_id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (user_id,)
    sql = '''
        DELETE
        FROM user
        WHERE id = (?)
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def user_id(line_id):
    conn = sqlite3.connect("database/portfolio_management.db")
    data = (line_id,)
    sql = '''
        SELECT id
        FROM user
        WHERE line_id = (?)
        '''
    result = conn.execute(sql, data).fetchone()
    return result[0]


def line_id(user_id):
    conn = sqlite3.connect("database/portfolio_management.db")
    data = (user_id,)
    sql = '''
        SELECT line_id
        FROM user
        WHERE id = (?)
        '''
    result = conn.execute(sql, data).fetchone()
    return result[0]


def read_risk_free_rate(user_id):
    conn = sqlite3.connect("database/portfolio_management.db")
    data = (user_id,)
    sql = '''
        SELECT risk_free_rate
        FROM user
        WHERE id = (?)
        '''
    cur = conn.execute(sql, data)
    result = cur.fetchone()

    return result[0]


def set_risk_free_rate(user_id, risk_free_rate):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (risk_free_rate, time.time(), user_id)
    sql = '''
        UPDATE user
        SET risk_free_rate = ?, update_time = ?
        WHERE id = ?
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


# def model_type(user_id):
#     conn = sqlite3.connect(os.path.join(globals.BASE_PATH, 'database', 'portfolio_management.db'))
#     data = (user_id,)
#     sql = '''
#         SELECT model_type
#         FROM user
#         WHERE id = (?)
#         '''
#     cur = conn.execute(sql, data)
#     result = cur.fetchone()
#     return None if result == None else result[0]


def set_model_type(user_id, model_type):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (model_type, user_id)
    sql = '''
        UPDATE user
        SET model_type = ?
        WHERE id = ?
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def set_risk_bound(user_id, risk_and_bound):
    conn = sqlite3.connect('database/portfolio_management.db')

    if 'risk_free_rate' in risk_and_bound:
        set_risk_free_rate(user_id, risk_and_bound['risk_free_rate'])

    risk_and_bound = json.dumps(risk_and_bound, indent=4)
    data = (risk_and_bound, time.time(), user_id)
    sql = '''
            UPDATE user
            SET args = ?, update_time = ?
            WHERE id = ?
            '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def read_update_time(id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (id,)
    sql = '''
            SELECT update_time 
            FROM user
            WHERE id = (?)
            '''
    update_time = conn.execute(sql, data).fetchone()
    conn.close()
    return update_time[0] if update_time else None


def read_args(id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (id,)
    sql = '''
            SELECT args 
            FROM user
            WHERE id = (?)
            '''
    update_time = conn.execute(sql, data).fetchone()
    conn.close()
    return update_time[0] if update_time else None


def update_update_time(id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (time.time(), id)
    sql = '''
                UPDATE user
                SET update_time = (?) 
                WHERE id = (?)
                '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()
    return None


def read_model_type(id):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (id,)
    sql = '''
                SELECT model_type 
                FROM user
                WHERE id = (?)
                '''
    update_time = conn.execute(sql, data).fetchone()
    conn.close()
    return update_time[0] if update_time else None
