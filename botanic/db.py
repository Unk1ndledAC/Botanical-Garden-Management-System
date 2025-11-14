from botanic.config import DB_CFG
import time
import pymysql
from pymysql.cursors import DictCursor

def _get_conn():
    return pymysql.connect(**DB_CFG, cursorclass=DictCursor)

def sql_query(sql, params=None, retry=3):
    for i in range(retry):
        try:
            with _get_conn() as conn, conn.cursor() as cur:
                cur.execute(sql, params or ())
                return cur.fetchall()
        except:
            if i == retry - 1:
                raise
            time.sleep(0.2)

def sql_execute(sql, params=None, retry=3):
    for i in range(retry):
        try:
            with _get_conn() as conn, conn.cursor() as cur:
                cur.execute(sql, params or ())
                conn.commit()
                return
        except:
            if i == retry - 1:
                raise
            time.sleep(0.2)

def test_connect():
    try:
        conn = _get_conn()
        with conn as c:
            cur = c.cursor()
            cur.execute("SELECT VERSION()")
            version = cur.fetchone()['VERSION()']
            print(f"[DB] 连接成功：{version}")
            return True
    except Exception as e:
        msg = f"数据库连接失败：{e}"
        print(msg)
        import tkinter.messagebox as mb
        mb.showerror("数据库连接异常", msg)
        return False