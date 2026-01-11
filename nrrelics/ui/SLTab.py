import os

import ttkbootstrap as tb
from pubsub import pub
from nrrelics.ui.BackupTree import BackupTree


class SLTab(tb.Frame):
    def __init__(self, master, config, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.use_auto_sl = config.use_auto_sl
        self.sl_threshold = config.sl_threshold
        self.keep_count_threshold = config.keep_count_threshold

        self.left_frame = tb.Frame(self)
        self.left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.right_frame = tb.Frame(self)
        self.right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        self.setup_left_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        self.auto_sl_var = tb.BooleanVar(value=self.use_auto_sl)
        self.auto_sl_checkbox = tb.Checkbutton(
            self.left_frame, 
            text='启用自动SL', 
            variable=self.auto_sl_var,
            command=self.toggle_auto_sl,
            bootstyle='round-toggle'
        )
        self.auto_sl_checkbox.pack(side='top', anchor='w', padx=10, pady=10)

        tb.Label(self.left_frame, text='SL阈值', font=('bold', 10)).pack(side='top', anchor='w', padx=10, pady=5)
        self.sl_threshold_var = tb.IntVar(value=self.sl_threshold)
        self.sl_threshold_spinbox = tb.Spinbox(
            self.left_frame, 
            from_=0, 
            to=10000000,
            increment=10000, 
            textvariable=self.sl_threshold_var,
            command=self.update_sl_threshold,
            width=15
        )
        self.sl_threshold_spinbox.pack(side='top', anchor='w', padx=10, pady=5)
        self.sl_threshold_var.trace_add("write", self.update_sl_threshold)
        tb.Label(self.left_frame, text='出货量阈值', font=('bold', 10)).pack(side='top', anchor='w', padx=10, pady=5)
        self.keep_count_var = tb.IntVar(value=self.keep_count_threshold)
        self.keep_count_spinbox = tb.Spinbox(
            self.left_frame, 
            from_=1, 
            to=1000,
            increment=1, 
            textvariable=self.keep_count_var,
            command=self.update_keep_count_threshold,
            width=15
        )
        self.keep_count_spinbox.pack(side='top', anchor='w', padx=10, pady=5)
        self.keep_count_var.trace_add("write", self.update_keep_count_threshold)


    def setup_right_panel(self):
        tb.Label(self.right_frame, text='备份列表', font=('bold', 10)).pack(side='top', anchor='w', padx=10, pady=5)
        btn = tb.Button(self.right_frame, text="设置为SL备份",command=self.select_sl_backup)
        self.backup_tree = BackupTree(self.right_frame, self.config.save_path, update_button=btn)
        self.backup_tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.backup_tree.refresh_tree()
        btn.pack(side='top', anchor='w', padx=10, pady=5)
        pub.subscribe(lambda p: self.backup_tree.set_watch_dir(p), "save_path_changed")

    def select_sl_backup(self):
        selected_file = self.backup_tree.get_selected_file()
        if os.path.exists(selected_file):
            self.config.sl_save_path = selected_file
            self.config.save()

    def toggle_auto_sl(self):
        self.use_auto_sl = self.auto_sl_var.get()
        self.config.use_auto_sl = self.use_auto_sl
        self.config.save()

    def update_sl_threshold(self, *args):
        try:
            self.sl_threshold = self.sl_threshold_var.get()
            self.config.sl_threshold = self.sl_threshold
            self.config.save()
        except Exception as e:
            pass

    def update_keep_count_threshold(self,*args):
        try:
            self.keep_count_threshold = self.keep_count_var.get()
            self.config.keep_count_threshold = self.keep_count_threshold
            self.config.save()
        except Exception as e:
            pass
