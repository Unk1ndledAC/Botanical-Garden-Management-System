import tkinter as tk
from tkinter import ttk, messagebox
from botanic.db import sql_query
from botanic.models import insert_guest_user
from botanic.ui_user import UserWin        
from botanic.ui_admin import AdminWin       

class LoginWin(tk.Tk):                     
    def __init__(self):
        super().__init__()
        self.title("植物园管理系统 - 登录")
        self.geometry("300x200")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="用户名").grid(row=0, column=0, padx=15, pady=10, sticky="e")
        ttk.Label(self, text="密码").grid(row=1, column=0, padx=15, pady=5, sticky="e")
        self.user_var = tk.StringVar()
        self.pwd_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.user_var).grid(row=0, column=1)
        ttk.Entry(self, textvariable=self.pwd_var, show="*").grid(row=1, column=1)

        ttk.Button(self, text="登录", command=self._check_login).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="访客入园", command=self._guest_entry).grid(row=3, column=0, columnspan=2, pady=5)

    def _check_login(self):
        user, pwd = self.user_var.get().strip(), self.pwd_var.get().strip()
        if not user or not pwd:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return
        row = sql_query("SELECT user_id, role FROM `user` WHERE username=%s AND password=%s", (user, pwd))
        if not row:
            messagebox.showerror("错误", "用户名或密码错误")
            return
        self._enter_system(row[0]["user_id"], row[0]["role"], user)

    def _guest_entry(self):
        GuestRegister(self)

    def _enter_system(self, uid: int, role: str, username: str):
        try:
            if role == "admin":
                top = AdminWin(uid, username)
            else:
                top = UserWin(uid, username)
        except Exception as e:                  
            messagebox.showerror("初始化失败", f"无法打开主界面：{e}")
            return                              
        self.withdraw()
        top.focus_force()
        self.wait_window(top)                   
        self.deiconify()                      

class GuestRegister(tk.Toplevel):
    def __init__(self, master: LoginWin):
        super().__init__(master)
        self.master = master
        self.title("访客登记")
        self.geometry("320x160")
        self.resizable(False, False)
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="昵称 *").grid(row=0, column=0, padx=15, pady=15, sticky="e")
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var, width=25).grid(row=0, column=1)

        ttk.Label(self, text="邮箱").grid(row=1, column=0, padx=15, pady=5, sticky="e")
        self.mail_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.mail_var, width=25).grid(row=1, column=1)

        ttk.Button(self, text="进入园区", command=self._do_enter).grid(row=2, column=0, columnspan=2, pady=20)

    def _do_enter(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "请填写昵称")
            return
        email = self.mail_var.get().strip() or None
        try:
            uid = insert_guest_user(name, email)
        except Exception as e:
            messagebox.showerror("错误", f"登记失败：{e}")
            return
        self.destroy()
        self.master._enter_system(uid, "guest", name)