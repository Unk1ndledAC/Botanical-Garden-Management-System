from botanic.ui_login import LoginWin
from botanic.db import sql_execute, init_schema
import traceback
def cleanup_guest_users():
    try:
        sql_execute("DELETE FROM `user` WHERE role = 'guest'")
        print("[DB] 已清理所有访客记录")
    except Exception as e:
        print(f"[DB] 清理访客记录失败：{e}")

if __name__ == '__main__':
    try:
        init_schema()
        cleanup_guest_users()
        root = LoginWin()
        root.mainloop()
    except Exception as e:
        traceback.print_exc()
        print(f"[System] 程序异常退出：{e}")
