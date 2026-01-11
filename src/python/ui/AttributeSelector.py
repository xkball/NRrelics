import ttkbootstrap as tb
from ttkbootstrap.constants import *

class AttributeSelector(tb.Frame):
    def __init__(self, master, all_items, title_left, title_right, bootstyle="primary", callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.all_items = all_items if all_items else []
        self.current_selection_ref = []
        self.callback = callback

        container = tb.Frame(self)
        container.pack(fill=BOTH, expand=True, padx=5, pady=5)

        frame_left = tb.Labelframe(container, text=title_left, bootstyle="secondary")
        frame_left.pack(side=LEFT, fill=BOTH, expand=True, padx=5)
        self.search_var = tb.StringVar()
        self.search_var.trace("w", self.filter_left)
        tb.Entry(frame_left, textvariable=self.search_var).pack(fill=X, padx=5, pady=5)
        self.tree_left = tb.Treeview(frame_left, show="tree", selectmode="extended")
        self.tree_left.pack(side=LEFT, fill=BOTH, expand=True)
        sb_left = tb.Scrollbar(frame_left, orient="vertical", command=self.tree_left.yview)
        sb_left.pack(side=RIGHT, fill=Y)
        self.tree_left.configure(yscrollcommand=sb_left.set)

        frame_mid = tb.Frame(container)
        frame_mid.pack(side=LEFT, fill=Y, padx=5, pady=50)
        tb.Button(frame_mid, text="添加 >>", command=self.add_item, bootstyle=bootstyle).pack(pady=10)
        tb.Button(frame_mid, text="<< 移除", command=self.remove_item, bootstyle="secondary").pack(pady=10)

        frame_right = tb.Labelframe(container, text=title_right, bootstyle=bootstyle)
        frame_right.pack(side=LEFT, fill=BOTH, expand=True, padx=5)
        self.tree_right = tb.Treeview(frame_right, show="tree", selectmode="extended")
        self.tree_right.pack(side=LEFT, fill=BOTH, expand=True)
        sb_right = tb.Scrollbar(frame_right, orient="vertical", command=self.tree_right.yview)
        sb_right.pack(side=RIGHT, fill=Y)
        self.tree_right.configure(yscrollcommand=sb_right.set)

        self.tree_left.bind("<Control-a>", lambda e: self.select_all(self.tree_left))
        self.tree_right.bind("<Control-a>", lambda e: self.select_all(self.tree_right))

        self.refresh()

    def select_all(self, tree):
        tree.selection_set(tree.get_children())
        return "break"

    def load_selection(self, selection_list_ref):
        self.current_selection_ref = selection_list_ref
        self.refresh()

    def update_source(self, new_items):
        self.all_items = new_items
        self.refresh()

    def filter_left(self, *args):
        self.refresh(self.search_var.get().lower())

    def refresh(self, search=""):
        for t in [self.tree_left, self.tree_right]:
            for x in t.get_children(): t.delete(x)

        for item in self.all_items:
            if item not in self.current_selection_ref and search in item.lower():
                self.tree_left.insert("", END, text=item)

        for item in self.current_selection_ref:
            self.tree_right.insert("", END, text=item)

    def add_item(self):
        for item in self.tree_left.selection():
            txt = self.tree_left.item(item, "text")
            if txt not in self.current_selection_ref:
                self.current_selection_ref.append(txt)
        self.refresh(self.search_var.get())
        if self.callback: self.callback()

    def remove_item(self):
        for item in self.tree_right.selection():
            txt = self.tree_right.item(item, "text")
            if txt in self.current_selection_ref:
                self.current_selection_ref.remove(txt)
        self.refresh(self.search_var.get())
        if self.callback: self.callback()

    def get_list(self):
        return self.current_selection_ref

