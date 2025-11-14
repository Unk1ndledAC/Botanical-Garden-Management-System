import tkinter as tk
from tkinter import ttk
from botanic.db import sql_query
from botanic.models import get_user_role

class UserWin(tk.Toplevel):
    def __init__(self, user_id: int, username: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.role = get_user_role(user_id)
        self.title(f"欢迎{'访客' if self.role == 'guest' else '用户'}：{username}")
        self.geometry("900x600")
        self._build_ui()
        self.refresh_plant_tree()
        
    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", padx=10, pady=10)
        ttk.Label(top, text="搜索中文名").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        ttk.Button(top, text="查询", command=self.refresh_plant_tree).pack(side="left", padx=5)
        ttk.Button(top, text="刷新全部", command=self.refresh_plant_tree).pack(side="left", padx=5)
        if self.role != "guest":
            ttk.Button(top, text="修改密码", command=self._change_pwd).pack(side="right", padx=5)

        columns = ("中文名", "描述", "产地", "生境", "花期", "用途")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        bottom = ttk.LabelFrame(self, text="该植物库存情况")
        bottom.pack(side="bottom", fill="both", expand=True, padx=10, pady=5)
        inv_cols = ("园区", "位置", "数量", "种植日期", "状态")
        self.inv_tree = ttk.Treeview(bottom, columns=inv_cols, show="headings", height=6)
        for col in inv_cols:
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=140, anchor="center")
        self.inv_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self._on_plant_select)
        
    def refresh_plant_tree(self):
        key = f"%{self.search_var.get().strip()}%"
        sql = """
        SELECT chinese_name, description, origin, habitat, bloom_period, use_type, plant_id
        FROM plant
        WHERE chinese_name LIKE %s
        ORDER BY plant_id DESC
        """
        rows = sql_query(sql, (key,))
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in rows:
            self.tree.insert("", "end", values=(r["chinese_name"],  r["description"],   r["origin"],
                                                r["habitat"],       r["bloom_period"],  r["use_type"]),
                                                                                    iid=r["plant_id"])
            
    def _on_plant_select(self, _event):
        pid = self.tree.focus()
        if not pid:
            return
        sql = """
        SELECT z.zone_name, z.location, pl.quantity, pl.planted_date, pl.status
        FROM plant_location pl
        JOIN zone z ON z.zone_id = pl.zone_id
        WHERE pl.plant_id = %s
        """
        rows = sql_query(sql, (pid,))
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        for r in rows:
            self.inv_tree.insert("", "end", values=(r["zone_name"], r["location"],
                                                    r["quantity"], r["planted_date"], r["status"]))
            
    def _change_pwd(self):
        from botanic.ui_admin import ChangePwd
        ChangePwd(self.user_id, self.username)
