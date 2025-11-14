from botanic.ui_login import LoginWin
from botanic.db import test_connect, sql_execute
import traceback

def cleanup_guest_users():
    try:
        sql_execute("DELETE FROM `user` WHERE role = 'guest'")
        print("[System] 已清理所有访客用户")
    except Exception as e:
        print(f"[System] 清理访客用户失败：{e}")

if __name__ == '__main__':
    try:
        if not test_connect():     
            print("数据库连接失败，请检查数据库连接")    
        cleanup_guest_users()
        root = LoginWin()
        root.mainloop()
    except Exception as e:
        traceback.print_exc()
        print(e)