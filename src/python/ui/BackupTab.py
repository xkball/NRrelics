import datetime
import os
import shutil

import ttkbootstrap as tb
from src.python.ui.BackupTree import BackupTree


class BackupTab(tb.Frame):
    def __init__(self,master, config, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.save_dir = config.save_path
        self.auto_backup = config.use_auto_backup

        self.path_var = tb.StringVar(value=self.save_dir)
        self.path_entry = tb.Entry(self, textvariable=self.path_var, state='readonly', width=50)
        self.path_entry.pack(side='top', fill = "x", anchor='w', padx=10, pady=5)

        self.edit_btn = tb.Button(self, text='编辑存档文件夹', bootstyle='outline', command=self.toggle_edit)
        self.edit_btn.pack(side='top', anchor="w", padx=10, pady=5)
        tb.Button(self, text='打开存档文件夹', bootstyle='outline', command=self.open_save_dir).pack(side='top', anchor="w", padx=10, pady=5)
        self.auto_backup_btn = tb.Checkbutton(self, text='启用每日自动备份', command=self.toggle_auto_backup, bootstyle='round-toggle', variable=tb.BooleanVar(value=self.auto_backup))
        self.auto_backup_btn.pack(side='top', anchor="w", padx=10, pady=5)
        tb.Button(self, text='手动备份', bootstyle='outline', command=self.runBackup).pack(side='top', anchor="w", padx=10, pady=5)

        self.restore_btn = tb.Button(self, text='恢复选中备份', bootstyle='success', state='disabled', command=self.restore_selected)
        self.backup_tree = BackupTree(self, self.save_dir, update_button=self.restore_btn)
        self.backup_tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.restore_btn.pack(side='left', padx=10, pady=5)

    def toggle_edit(self):
        if self.path_entry.cget('state') == 'readonly':
            self.path_entry.configure(state='normal')
            self.edit_btn.configure(text='保存')
        else:
            new_path = self.path_var.get().strip()
            if os.path.isdir(new_path):
                self.save_dir = new_path
                self.config.save_path = self.save_dir
                self.config.save()
                self.path_entry.configure(state='readonly')
                self.edit_btn.configure(text='编辑存档文件夹')
                self.backup_tree.set_watch_dir(self.save_dir)

    def toggle_auto_backup(self):
        self.auto_backup = self.auto_backup_btn.instate(['selected'])
        self.config.use_auto_backup = self.auto_backup
        self.config.save()
        self.check_auto_backup()
        
    def check_auto_backup(self):
        if not self.auto_backup:
            return
        
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        has_today_backup = False
        
        for backup in self.backup_tree.all_backups:
            backup_date = backup['time'].split(' ')[0]
            if backup_date == today:
                has_today_backup = True
                break
        
        if not has_today_backup:
            self.runBackup()

    def open_save_dir(self):
        if os.path.isdir(self.save_dir):
            os.startfile(self.save_dir)

    def restore_selected(self):
        src_path = self.backup_tree.get_selected_file()
        if not src_path:
            return
        if not os.path.isfile(src_path):
            return
        dst_path = os.path.join(self.save_dir, os.path.basename(src_path))
        self.runBackup(base="restore")
        try:
            shutil.copy2(src_path, dst_path)

            print(f"已恢复备份备份：{src_path} -> {dst_path}")
        except (IOError, OSError) as e:
            print(f"恢复备份失败：{e}")
            pass

    @staticmethod
    def getDefaultSavePath():
        appdata = os.environ["APPDATA"]
        dir_ = os.path.join(appdata, "Nightreign")
        try:
            for item in os.listdir(dir_):
                item_path = os.path.join(dir_, item)
                if os.path.isdir(item_path):
                    for file in os.listdir(item_path):
                        if file.endswith('.sl2'):
                            return item_path
        except (PermissionError, OSError):
            return ""
        return ""

    def runBackup(self, base = "backup"):
        BackupTab.runBackupStatic(self.save_dir, base)
        self.backup_tree.refresh_tree()

    @staticmethod
    def runBackupStatic(save_dir, base = "backup", check_exists = False):
        src = None
        candidate = os.path.join(save_dir, "NR0000.sl2")
        if os.path.isfile(candidate):
            src = candidate
        else:
            try:
                for f in os.listdir(save_dir):
                    if f.endswith(".sl2"):
                        src = os.path.join(save_dir, f)
                        break
            except (PermissionError, OSError):
                pass

        if not src:
            print("错误：未找到NR0000.sl2或任何.sl2文件")
            return

        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")
        if check_exists and os.path.exists(os.path.join(save_dir,base,date_str)):
            return
        time_str = now.strftime("%H_%M_%S")
        backup_dir = os.path.join(save_dir, base, date_str, time_str)
        os.makedirs(backup_dir, exist_ok=True)

        dst = os.path.join(backup_dir, os.path.basename(src))
        try:
            shutil.copy2(src, dst)
            print(f"已备份：{src} -> {dst}")
        except (IOError, OSError) as e:
            print(f"备份失败：{e}")