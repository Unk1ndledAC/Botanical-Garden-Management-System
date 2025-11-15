import tkinter as tk
from tkinter import ttk, messagebox
from botanic.db import sql_query, sql_execute

class AdminWin(tk.Toplevel):
    def __init__(self, user_id: int, username: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.title(f"欢迎管理员：{username}")
        self.geometry("900x600")
        self._build_ui()

    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=5)

        frm_plant = ttk.Frame(nb)
        nb.add(frm_plant, text="植物维护")
        PlantCRUD(frm_plant)

        frm_zone = ttk.Frame(nb)
        nb.add(frm_zone, text="园区维护")
        ZoneCRUD(frm_zone)

        frm_stock = ttk.Frame(nb)
        nb.add(frm_stock, text="库存维护")
        StockCRUD(frm_stock)
        
        frm_pwd = ttk.Frame(nb)
        nb.add(frm_pwd, text="修改密码")
        ChangePwd(frm_pwd, self.user_id, self.username)
        
class PlantCRUD:
    def __init__(self, parent):
        self.parent = parent
        self._build_ui()
        self.refresh()
    def _build_ui(self):
        top = ttk.Frame(self.parent)
        top.pack(side="top", fill="x", padx=5, pady=5)
        ttk.Button(top, text="新增植物", command=self.add_plant).pack(side="left", padx=5)
        ttk.Button(top, text="编辑选中", command=self.edit_plant).pack(side="left", padx=5)
        ttk.Button(top, text="删除选中", command=self.del_plant).pack(side="left", padx=5)

        columns = ("ID", "中文名", "描述", "产地", "生境", "花期", "用途")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = sql_query("SELECT plant_id, chinese_name, description, origin, habitat, bloom_period, use_type AS use_type FROM plant")
        for r in rows:
            self.tree.insert("", "end", values=(r["plant_id"],  r["chinese_name"],  r["description"], r["origin"], 
                                                r["habitat"],   r["bloom_period"],  r["use_type"]))
    def add_plant(self):
        PlantEdit(self.parent, self, mode="add")
        self.refresh()
        
    def edit_plant(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先选中一行")
            return

        values = self.tree.item(selected_item, "values")
        plant_id = values[0]
        PlantEdit(self.parent, self, mode="edit", pid=plant_id)
        self.refresh()

    def del_plant(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先选中一行")
            return

        values = self.tree.item(selected_item, "values")
        plant_id = values[0]

        if messagebox.askyesno("确认", "确定删除？"):
            sql_execute("DELETE FROM plant WHERE plant_id=%s", (plant_id,))
            self.refresh()

class PlantEdit(tk.Toplevel):
    def __init__(self, parent_wnd, crud_instance, mode: str, pid=None):
        super().__init__(parent_wnd)
        self.crud = crud_instance
        self.mode = mode
        self.pid = pid
        self.title("新增/编辑植物")
        self.geometry("500x600")
        self._build_ui()
        if mode == "edit":
            self._load_old()
        self.grab_set()

    def _build_ui(self):
        ttk.Label(self, text="属").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.genus_dict = {r["genus_name"]: r["genus_id"] for r in
                          sql_query("SELECT genus_id, genus_name FROM taxonomy_genus")}
        self.genus_cb = ttk.Combobox(self, values=list(self.genus_dict.keys()), state="readonly", width=25)
        self.genus_cb.grid(row=0, column=1, sticky="w")

        labels = ["种加词", "中文名", "描述", "产地", "生境", "花期", "用途"]
        self.vars = [tk.StringVar() for _ in range(len(labels))]
        for idx, lab in enumerate(labels):
            ttk.Label(self, text=lab).grid(row=idx + 1, column=0, sticky="e", padx=5, pady=5)
            ttk.Entry(self, textvariable=self.vars[idx], width=50).grid(row=idx + 1, column=1, sticky="w")

        ttk.Button(self, text="保存", command=self._save).grid(row=len(labels) + 1, column=0, columnspan=2, pady=15)

    def _load_old(self):
        r = sql_query("SELECT * FROM plant WHERE plant_id=%s", (self.pid,))[0]
        self.genus_cb.set(
            sql_query("SELECT genus_name FROM taxonomy_genus WHERE genus_id=%s", (r["genus_id"],))[0]["genus_name"])
        for i, k in enumerate(["species_name", "chinese_name", "description", "origin", "habitat", "bloom_period", "use_type"]):
            self.vars[i].set(r[k] or "")

    def _save(self):
        gid = self.genus_dict[self.genus_cb.get()]
        vals = [v.get() for v in self.vars]
        if not all([gid, vals[0], vals[1]]):
            messagebox.showwarning("提示", "属、种加词、中文名必填")
            return
        if self.mode == "add":
            sql = """INSERT INTO plant(genus_id,species_name,chinese_name,description,origin,habitat,bloom_period,use_type)
                     VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
            sql_execute(sql, (gid, *vals))
        else:
            sql = """UPDATE plant SET genus_id=%s, species_name=%s, chinese_name=%s, description=%s,
                     origin=%s, habitat=%s, bloom_period=%s, use_type=%s WHERE plant_id=%s"""
            sql_execute(sql, (gid, *vals, self.pid))
        self.destroy()
        self.crud.refresh()

class ZoneCRUD:
    def __init__(self, parent):
        self.parent = parent
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top = ttk.Frame(self.parent)
        top.pack(side="top", fill="x", padx=5, pady=5)
        ttk.Button(top, text="新增园区", command=self.add_zone).pack(side="left", padx=5)
        ttk.Button(top, text="编辑选中", command=self.edit_zone).pack(side="left", padx=5)
        ttk.Button(top, text="删除选中", command=self.del_zone).pack(side="left", padx=5)

        columns = ("ID", "园区名", "位置", "简介")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = sql_query("SELECT zone_id, zone_name, location, intro FROM zone")
        for r in rows:
            self.tree.insert("", "end", values=(r["zone_id"], r["zone_name"], r["location"], r["intro"]))

    def add_zone(self):
        ZoneEdit(self.parent, self, mode="add")
        self.refresh()

    def edit_zone(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先选中一行")
            return
        
        values = self.tree.item(selected_item, "values")
        zone_id = values[0]
        ZoneEdit(self.parent, self, mode="edit", zid=zone_id)
        self.refresh()

    def del_zone(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先选中一行")
            return

        values = self.tree.item(selected_item, "values")
        zone_id = values[0]

        if messagebox.askyesno("确认", "确定删除？"):
            sql_execute("DELETE FROM zone WHERE zone_id=%s", (zone_id,))
            self.refresh()

class ZoneEdit(tk.Toplevel):
    def __init__(self, parent_wnd, crud_instance, mode: str, zid=None):
        super().__init__(parent_wnd)
        self.crud = crud_instance
        self.mode = mode
        self.zid = zid
        self.title("新增/编辑园区")
        self.geometry("400x300")
        self._build_ui()
        if mode == "edit":
            self._load_old()
        self.grab_set()

    def _build_ui(self):
        labels = ["园区名", "位置", "简介"]
        self.vars = [tk.StringVar() for _ in range(3)]
        for idx, lab in enumerate(labels):
            ttk.Label(self, text=lab).grid(row=idx, column=0, sticky="e", padx=5, pady=5)
            ttk.Entry(self, textvariable=self.vars[idx], width=40).grid(row=idx, column=1, sticky="w")
        ttk.Button(self, text="保存", command=self._save).grid(row=3, column=0, columnspan=2, pady=15)

    def _load_old(self):
        r = sql_query("SELECT * FROM zone WHERE zone_id=%s", (self.zid,))[0]
        for i, k in enumerate(["zone_name", "location", "intro"]):
            self.vars[i].set(r[k] or "")

    def _save(self):
        vals = [v.get() for v in self.vars]
        if not vals[0]:
            messagebox.showwarning("提示", "园区名必填")
            return
        if self.mode == "add":
            sql_execute("INSERT INTO zone(zone_name,location,intro) VALUES(%s,%s,%s)", vals)
        else:
            sql_execute("UPDATE zone SET zone_name=%s, location=%s, intro=%s WHERE zone_id=%s", (*vals, self.zid))
        self.destroy()
        self.crud.refresh()

class StockCRUD:
    def __init__(self, parent):
        self.parent = parent
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top = ttk.Frame(self.parent)
        top.pack(side="top", fill="x", padx=5, pady=5)
        ttk.Button(top, text="新增库存记录", command=self.add_stock).pack(side="left", padx=5)
        ttk.Button(top, text="编辑选中", command=self.edit_stock).pack(side="left", padx=5)
        ttk.Button(top, text="删除选中", command=self.del_stock).pack(side="left", padx=5)

        columns = ("ID", "中文名", "园区", "数量", "种植日期", "状态")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        sql = """
        SELECT pl.loc_id, p.chinese_name, z.zone_name, pl.quantity, pl.planted_date, pl.status
        FROM plant_location pl
        JOIN plant p ON p.plant_id = pl.plant_id
        JOIN zone z ON z.zone_id = pl.zone_id
        """
        rows = sql_query(sql)
        for r in rows:
            self.tree.insert("", "end", values=(r["loc_id"],    r["chinese_name"],  r["zone_name"],
                                                r["quantity"],  r["planted_date"],  r["status"]))

    def add_stock(self):
        StockEdit(self.parent, self, mode="add")
        self.refresh()

    def edit_stock(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先选中一行")
            return
        
        values = self.tree.item(selected_item, "values")
        loc_id = values[0]
        StockEdit(self.parent, self, mode="edit", lid=loc_id)
        self.refresh()

    def del_stock(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先选中一行")
            return
        
        values = self.tree.item(selected_item, "values")
        loc_id = values[0]
        if messagebox.askyesno("确认", "确定删除该库存记录？"):
            sql_execute("DELETE FROM plant_location WHERE loc_id=%s", (loc_id,))
            self.refresh()

class StockEdit(tk.Toplevel):
    def __init__(self, parent_wnd, crud_instance, mode: str, lid=None):
        super().__init__(parent_wnd)
        self.crud = crud_instance
        self.mode = mode
        self.lid = lid
        self.title("新增/编辑库存")
        self.geometry("500x350")
        self._build_ui()
        if mode == "edit":
            self._load_old()
        self.grab_set()

    def _build_ui(self):
        ttk.Label(self, text="植物").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.plant_dict = {r["chinese_name"]: r["plant_id"] for r in
                          sql_query("SELECT plant_id, chinese_name FROM plant")}
        self.plant_cb = ttk.Combobox(self, values=list(self.plant_dict.keys()), state="readonly", width=40)
        self.plant_cb.grid(row=0, column=1, sticky="w")

        ttk.Label(self, text="园区").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.zone_dict = {r["zone_name"]: r["zone_id"] for r in sql_query("SELECT zone_id, zone_name FROM zone")}
        self.zone_cb = ttk.Combobox(self, values=list(self.zone_dict.keys()), state="readonly", width=25)
        self.zone_cb.grid(row=1, column=1, sticky="w")

        labels = ["数量", "种植日期(YYYY-MM-DD)", "状态"]
        self.vars = [tk.StringVar() for _ in range(3)]
        self.vars[2].set("healthy")
        for idx, lab in enumerate(labels):
            ttk.Label(self, text=lab).grid(row=idx + 2, column=0, sticky="e", padx=5, pady=5)
            if idx == 2:
                ttk.Combobox(self, textvariable=self.vars[idx], values=("healthy", "poor", "dead"), state="readonly",
                            width=20).grid(row=idx + 2, column=1, sticky="w")
            else:
                ttk.Entry(self, textvariable=self.vars[idx], width=25).grid(row=idx + 2, column=1, sticky="w")

        ttk.Button(self, text="保存", command=self._save).grid(row=5, column=0, columnspan=2, pady=15)

    def _load_old(self):
        r = sql_query("SELECT * FROM plant_location WHERE loc_id=%s", (self.lid,))[0]
        self.plant_cb.set(sql_query("SELECT chinese_name FROM plant WHERE plant_id=%s",
                                   (r["plant_id"],))[0]["chinese_name"])
        self.zone_cb.set(sql_query("SELECT zone_name FROM zone WHERE zone_id=%s", (r["zone_id"],))[0]["zone_name"])
        for i, k in enumerate(["quantity", "planted_date", "status"]):
            self.vars[i].set(r[k])

    def _save(self):
        pid = self.plant_dict[self.plant_cb.get()]
        zid = self.zone_dict[self.zone_cb.get()]
        qty, dt, st = self.vars[0].get(), self.vars[1].get(), self.vars[2].get()
        if not (pid and zid and qty and dt and st):
            messagebox.showwarning("提示", "请填写完整")
            return
        if self.mode == "add":
            sql_execute("INSERT INTO plant_location(plant_id,zone_id,quantity,planted_date,status) VALUES(%s,%s,%s,%s,%s)",
                       (pid, zid, qty, dt, st))
        else:
            sql_execute("UPDATE plant_location SET plant_id=%s, zone_id=%s, quantity=%s, planted_date=%s, status=%s WHERE loc_id=%s",
                       (pid, zid, qty, dt, st, self.lid))
        self.destroy()
        self.crud.refresh()

class ChangePwd(ttk.Frame):
    def __init__(self, parent, user_id: int, username: str):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.pack(fill="both", expand=True)
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self)
        frm.pack(pady=40)

        ttk.Label(frm, text="新密码").grid(row=0, column=0, padx=15, pady=15, sticky="e")
        self.p1 = tk.StringVar()
        ttk.Entry(frm, textvariable=self.p1, show="*").grid(row=0, column=1)

        ttk.Label(frm, text="再输入").grid(row=1, column=0, padx=15, pady=5, sticky="e")
        self.p2 = tk.StringVar()
        ttk.Entry(frm, textvariable=self.p2, show="*").grid(row=1, column=1)

        ttk.Button(frm, text="确认修改", command=self._save).grid(row=2, column=0, columnspan=2, pady=20)

    def _save(self):
        p1, p2 = self.p1.get(), self.p2.get()
        if p1 != p2:
            messagebox.showwarning("提示", "两次输入不一致")
            return
        sql_execute("UPDATE `user` SET password=%s WHERE user_id=%s", (p1, self.user_id))
        messagebox.showinfo("成功", "密码已修改")
