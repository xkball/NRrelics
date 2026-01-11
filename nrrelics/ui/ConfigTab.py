import os

import ttkbootstrap as tb

from nrrelics.data.Config import Config


class ConfigTab(tb.Frame):
    def __init__(self, master, config = Config, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.btn = tb.Button(self, text="打开配置文件夹", command=lambda : os.startfile(os.path.dirname(self.config.get_config_file())))
        self.btn.pack(side='top', anchor='w', padx=10, pady=5)