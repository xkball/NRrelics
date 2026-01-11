import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import simpledialog, filedialog, messagebox

from src.python.ui.AttributeSelector import AttributeSelector


class PresetEditor(tb.Frame):
    def __init__(self, master, all_possible_items, **kwargs):
        super().__init__(master, **kwargs)
        self.presets = []
        self.current_preset_index = -1
        self.all_possible_items = all_possible_items

        left_panel = tb.Frame(self, width=220)
        left_panel.pack(side=LEFT, fill=Y, padx=5, pady=5)

        toolbar1 = tb.Frame(left_panel)
        toolbar1.pack(fill=X, pady=2)
        tb.Button(toolbar1, text="+", width=3, command=self.add_preset, bootstyle="success-outline").pack(side=LEFT,
                                                                                                          padx=1)
        tb.Button(toolbar1, text="-", width=3, command=self.del_preset, bootstyle="danger-outline").pack(side=LEFT,
                                                                                                         padx=1)
        tb.Button(toolbar1, text="改名", width=5, command=self.rename_preset, bootstyle="info-outline").pack(side=LEFT,
                                                                                                             padx=1)

        self.lb_presets = tb.Treeview(left_panel, show="tree", selectmode="browse")
        self.lb_presets.pack(fill=BOTH, expand=True)
        self.lb_presets.bind("<<TreeviewSelect>>", self.on_preset_select)

        self.selector = AttributeSelector(
            self,
            self.all_possible_items,
            "词条库",
            "当前预设包含的词条 (>=2生效)",
            "success"
        )
        self.selector.pack(side=RIGHT, fill=BOTH, expand=True)

    def load_presets(self, presets_data):
        self.presets = presets_data
        if not self.presets:
            self.presets.append({"name": "默认预设", "items": []})
        self.refresh_list()
        if self.presets:
            first_id = self.lb_presets.get_children()[0]
            self.lb_presets.selection_set(first_id)

    def refresh_list(self):
        selected = self.lb_presets.selection()
        selected_idx = self.lb_presets.index(selected[0]) if selected else 0

        for item in self.lb_presets.get_children():
            self.lb_presets.delete(item)

        for p in self.presets:
            count = len(p["items"])
            self.lb_presets.insert("", END, text=f"{p['name']} ({count})")

        children = self.lb_presets.get_children()
        if 0 <= selected_idx < len(children):
            self.lb_presets.selection_set(children[selected_idx])
        elif children:
            self.lb_presets.selection_set(children[0])

    def on_preset_select(self, event):
        selected = self.lb_presets.selection()
        if not selected: return
        idx = self.lb_presets.index(selected[0])
        self.current_preset_index = idx
        self.selector.load_selection(self.presets[idx]["items"])

    def add_preset(self):
        if len(self.presets) >= 10: return
        new_name = f"预设 {len(self.presets) + 1}"
        self.presets.append({"name": new_name, "items": []})
        self.refresh_list()
        last = self.lb_presets.get_children()[-1]
        self.lb_presets.selection_set(last)

    def del_preset(self):
        if len(self.presets) <= 1: return
        if self.current_preset_index >= 0:
            del self.presets[self.current_preset_index]
            self.refresh_list()

    def rename_preset(self):
        if self.current_preset_index < 0: return
        old_name = self.presets[self.current_preset_index]["name"]
        new_name = simpledialog.askstring("重命名", "请输入预设名称:", initialvalue=old_name)
        if new_name:
            self.presets[self.current_preset_index]["name"] = new_name
            self.refresh_list()

    def export_presets(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    import json
                    json.dump(self.presets, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("成功", f"导出成功")
            except Exception as e:
                messagebox.showerror("错误", str(e))

    def import_presets(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    import json
                    data = json.load(f)
                self.presets = data
                self.refresh_list()
                messagebox.showinfo("成功", "导入成功")
            except Exception as e:
                messagebox.showerror("错误", str(e))

    def update_source_library(self, new_library):
        self.all_possible_items = new_library
        self.selector.update_source(new_library)

    def get_presets(self):
        return self.presets
