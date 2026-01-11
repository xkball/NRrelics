import datetime
import os
import ttkbootstrap as tb

class BackupTree(tb.Frame):
    def __init__(self, master, watch_dir, update_button=None, **kwargs):
        super().__init__(master, **kwargs)
        self.watch_dir = watch_dir
        self.update_button = update_button
        self.all_backups = []
        self.update_button.configure(state='disabled')
        self.tree_frame = tb.Frame(self)
        self.tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.backup_tree = tb.Treeview(self.tree_frame, columns=('size', 'mtime', 'btime'), height=10, show='tree headings')
        self.backup_tree.heading('#0', text='备份文件')
        self.backup_tree.heading('size', text='大小')
        self.backup_tree.heading('mtime', text='修改时间')
        self.backup_tree.heading('btime', text='备份时间')
        self.backup_tree.column('size', width=80, anchor='center')
        self.backup_tree.column('mtime', width=140, anchor='center')
        self.backup_tree.column('btime', width=140, anchor='center')
        self.backup_tree.pack(side='left', fill='both', expand=True)

        tree_scroll = tb.Scrollbar(self.tree_frame, orient='vertical', command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side='right', fill='y')

        self.backup_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.refresh_tree()
    
    def set_watch_dir(self, new_dir):
        self.watch_dir = new_dir
        self.refresh_tree()
    
    def get_watch_dir(self):
        return self.watch_dir
    
    def refresh_tree(self):
        self.all_backups.clear()
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)

        backup_root = os.path.join(self.watch_dir, 'backup')
        if not os.path.isdir(backup_root):
            return

        for date_folder in sorted(os.listdir(backup_root), reverse=True):
            date_path = os.path.join(backup_root, date_folder)
            if not os.path.isdir(date_path):
                continue
            
            for time_folder in sorted(os.listdir(date_path), reverse=True):
                time_path = os.path.join(date_path, time_folder)
                if not os.path.isdir(time_path):
                    continue
                
                for file in os.listdir(time_path):
                    if file.endswith('.sl2'):
                        file_path = os.path.join(time_path, file)
                        stat = os.stat(file_path)
                        size = f'{stat.st_size / 1024:.1f} KB'
                        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        backup_time = f"{date_folder[:4]}-{date_folder[4:6]}-{date_folder[6:]} {time_folder.replace('_', ':')}"
                        self.backup_tree.insert('', 'end', text=file, values=(size, mtime, backup_time), tags=(file_path,))
                        self.all_backups.append({'time': backup_time, 'file': file_path})
    
    def on_tree_select(self, event):
        selection = self.backup_tree.selection()
        if selection:
            file_path = self.backup_tree.item(selection[0], 'tags')[0]
            if file_path.endswith('.sl2'):
                if self.update_button:
                    self.update_button.configure(state='normal')
            else:
                if self.update_button:
                    self.update_button.configure(state='disabled')
        else:
            if self.update_button:
                self.update_button.configure(state='disabled')
    
    def get_selected_file(self):
        selection = self.backup_tree.selection()
        if selection:
            return self.backup_tree.item(selection[0], 'tags')[0]
        return None

