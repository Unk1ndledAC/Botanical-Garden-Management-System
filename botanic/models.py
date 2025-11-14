from botanic.db import sql_query, sql_execute

def get_user_role(uid: int) -> str:
    row = sql_query("SELECT role FROM `user` WHERE user_id=%s", (uid,))
    return row[0]["role"] if row else "guest"

def insert_guest_user(name: str, email: str | None) -> int:
    sql_execute(
        "INSERT INTO `user`(username,password,email,role) VALUES(%s,%s,%s,'guest')",
        (name, "guest", email)
    )
    row = sql_query("SELECT user_id FROM `user` WHERE username=%s ORDER BY user_id DESC LIMIT 1", (name,))
    return row[0]["user_id"]