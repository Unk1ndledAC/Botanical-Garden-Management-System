from botanic.config import DB_CFG
import time, os, re
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

def create_database_if_not_exists():
    cfg = DB_CFG.copy()
    cfg.pop('database')
    conn = pymysql.connect(**cfg)
    try: 
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CFG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        print(f"[DB] 数据库 {DB_CFG['database']} 已创建")
    except Exception as e:
        msg = f"数据库连接失败：{e}"
        print(f"[System] {msg}")
        import tkinter.messagebox as mb
        mb.showerror("数据库连接异常", msg)
        print(f"[DB] 数据库 {DB_CFG['database']} 创建失败")
    finally:
        conn.close()

def init_schema(sql_file='schema.sql', data_file='data.sql'):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, '..', sql_file)
    schema_path = os.path.abspath(schema_path)

    data_path = os.path.join(base_dir, '..', data_file)
    data_path = os.path.abspath(data_path)

    create_database_if_not_exists()

    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT VERSION()")
                version = cur.fetchone()['VERSION()']
                print(f"[System] 成功连接数据库 {DB_CFG['database']}，版本：{version}")
    except Exception as e:
        print(f"[System] 连接数据库 {DB_CFG['database']} 失败：{e}")
        raise
    
    if os.path.exists(schema_path):
        with open(schema_path, encoding='utf-8') as f:
            content = f.read()

        paragraphs = re.split(r'^\s*DELIMITER\s+(\S+)\s*$', content, flags=re.M)
        delimiter = ';'
        conn = _get_conn()
        try:
            with conn.cursor() as cur:
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    if len(para) <= 5 and re.match(r'\S+$', para):
                        delimiter = para
                        continue
                    for stmt in para.split(delimiter):
                        stmt = stmt.strip()
                        if not stmt:
                            continue
                        cur.execute(stmt)
            conn.commit()
            print("[DB] 数据库 schema 初始化完成")
        except Exception as e:
            conn.rollback()
            print(f"[DB] 初始化失败：{e}")
        finally:
            conn.close()
    else:
        print(f"[DB] 未找到 {schema_path}，跳过建表")

    if os.path.exists(data_path):
        conn = _get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS c FROM `user`")
                if cur.fetchone()['c'] == 0:
                    with open(data_path, encoding='utf-8') as f:
                        content = f.read()
                        
                    statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
                    for stmt in statements:
                        if stmt.lower().startswith('use'):
                            continue
                        try:
                            cur.execute(stmt)
                        except Exception as e:
                            print(f"[DB] 执行语句失败：{stmt[:100]}... -> {e}")
                            raise
                    conn.commit()
                    print("[DB] 初始数据插入完成")
                else:
                    print("[DB] 数据已存在，跳过初始数据插入")
        except Exception as e:
            conn.rollback()
            print(f"[DB] 数据插入失败：{e}")
        finally:
            conn.close()
