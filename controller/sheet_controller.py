import sqlite3


def create(user_id, num_questions):
    answers = [-1 for _ in range(num_questions)]
    conn = sqlite3.connect('database/portfolio_management.db')
    data = [user_id, ] + answers

    sql = '''
        INSERT
        INTO sheet_ans (user_id, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def delete(user_id):
    conn = sqlite3.connect("database/portfolio_management.db")
    data = (user_id,)
    sql = '''
        DELETE
        FROM sheet_ans
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
        FROM sheet_ans
        WHERE user_id = (?)
        '''
    cur = conn.execute(sql, data)
    result = cur.fetchone()
    return result if result else None


def write(user_id, question_num, answer):
    conn = sqlite3.connect('database/portfolio_management.db')
    data = (answer, user_id)
    sql = f"UPDATE sheet_ans SET Q{question_num} = ? WHERE user_id = ?"
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def cursor(user_id):
    answers = read(user_id)
    try:
        return answers.index(-1)
    except ValueError:
        return False
