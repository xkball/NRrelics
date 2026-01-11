import sys
import threading
import time

import keyboard
import ttkbootstrap as tb
from apscheduler.schedulers.background import BackgroundScheduler
from ttkbootstrap.constants import *

from nrrelics.core.bot import BotLogic
from nrrelics.data.Config import Config
from nrrelics.data.loader import DataLoader
from nrrelics.ui.AttributeSelector import AttributeSelector
from nrrelics.ui.BackupTab import BackupTab
from nrrelics.ui.ConfigTab import ConfigTab
from nrrelics.ui.SLTab import SLTab
from nrrelics.ui.PresetEditor import PresetEditor


class App(tb.Window):

    def __init__(self):
        super().__init__(themename="superhero")
        self.title("NRrelic_bot V1.1")
        self.geometry("1100x850")

        self.norm_pos, self.deep_pos, self.deep_neg = DataLoader.get_data()
        self.logic = None
        self.config = Config()
        self.config.load()
        self.setup_ui()
        self.load_config()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # noinspection PyAttributeOutsideInit
    def setup_ui(self):
        top = tb.Frame(self)
        top.pack(fill=X, padx=10, pady=10)
        tb.Label(top, text="选择模式", font=("bold", 12)).pack(side=LEFT)
        self.mode_var = tb.StringVar(value="deepnight")
        rb1 = tb.Radiobutton(top, text="普通遗物", variable=self.mode_var, value="normal", command=self.on_mode_change)
        rb1.pack(side=LEFT, padx=15)
        rb2 = tb.Radiobutton(top, text="深夜遗物", variable=self.mode_var, value="deepnight",
                             command=self.on_mode_change)
        rb2.pack(side=LEFT, padx=15)

        self.nb = tb.Notebook(self)
        self.nb.pack(fill=BOTH, expand=True, padx=10)
        self.tab1 = tb.Frame(self.nb)
        self.nb.add(self.tab1, text="1. 策略预设")
        self.ui_presets = PresetEditor(self.tab1, [])
        self.ui_presets.pack(fill=BOTH, expand=True)

        self.tab2 = tb.Frame(self.nb)
        self.nb.add(self.tab2, text="2. 全局致命负面")
        self.ui_neg = AttributeSelector(self.tab2, self.deep_neg, "负面词条", "黑名单(出现即卖)", "danger")
        self.ui_neg.pack(fill=BOTH, expand=True)

        self.tab3 = tb.Frame(self.nb)
        self.nb.add(self.tab3, text="3. 自动备份")
        self.ui_backup = BackupTab(self.tab3, self.config)
        self.ui_backup.pack(fill=BOTH, expand=True)

        self.tab4 = tb.Frame(self.nb)
        self.nb.add(self.tab4, text="4. 自动SL")
        self.ui_sl = SLTab(self.tab4, self.config)
        self.ui_sl.pack(fill=BOTH, expand=True)

        self.tab5 = tb.Frame(self.nb)
        self.nb.add(self.tab5, text="5. 配置文件")
        self.ui_config = ConfigTab(self.tab5, self.config)
        self.ui_config.pack(fill=BOTH, expand=True)
        
        ctrl = tb.Frame(self)
        ctrl.pack(fill=X, padx=20, pady=20)
        self.btn_start = tb.Button(ctrl, text="开始挂机", command=self.start, bootstyle="success")
        self.btn_start.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.btn_stop = tb.Button(ctrl, text="停止 (F11)", command=self.stop, bootstyle="danger", state="disabled")
        self.btn_stop.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.log_text = tb.Text(self, height=8)
        self.log_text.pack(fill=X, padx=20, pady=10)

    def on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "normal":
            self.ui_presets.update_source_library(self.norm_pos)
            self.ui_presets.load_presets(self.config.presets_norm)
            self.nb.tab(1, state="disabled")
        else:
            self.ui_presets.update_source_library(self.deep_pos)
            self.ui_presets.load_presets(self.config.presets_deep)
            self.nb.tab(1, state="normal")

    def log(self, msg):
        self.log_text.insert(END, msg + "\n")
        self.log_text.see(END)

    def start(self):
        current_presets = self.ui_presets.get_presets()
        if not current_presets:
            self.log("错误：请至少添加一套预设策略！")
            return
        config = {'mode': self.mode_var.get(), 'presets': current_presets, 'bad_neg': self.ui_neg.get_list()}
        self.save_to_json()
        self.logic = BotLogic(self.log, self.config)
        t = threading.Thread(target=self.logic.run, args=(config,))
        t.daemon = True
        t.start()
        threading.Thread(target=self.monitor_keys, daemon=True).start()
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")

    def monitor_keys(self):
        while self.logic and not self.logic.should_stop:
            if keyboard.is_pressed('f11'): self.stop(); break
            time.sleep(0.1)

    def stop(self):
        if self.logic: self.logic.should_stop = True
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    def save_to_json(self):
        mode = self.mode_var.get()
        current_data = self.ui_presets.get_presets()
        if mode == "normal":
            self.config.presets_norm = current_data
        else:
            self.config.presets_deep = current_data
        self.config.last_mode = mode
        self.config.bad_neg = self.ui_neg.get_list()
        self.config.save()

    def load_config(self):
        # 修复：AttributeSelector没有set_list方法，需要直接设置current_selection_ref
        self.ui_neg.current_selection_ref = self.config.bad_neg
        self.ui_neg.refresh()
        self.mode_var.set(self.config.last_mode)
        self.on_mode_change()
        self.ui_backup.check_auto_backup()
    
    def on_closing(self):
        self.save_to_json()
        self.destroy()


if __name__ == "__main__":
    def check_backup():
        config = Config()
        config.load()
        if config.use_auto_backup:
            BackupTab.runBackupStatic(config.save_path, check_exists=True)

    if len(sys.argv) == 2:
        if sys.argv[1] == "-check_backup":
            print("正在检查备份...")
            check_backup()
            time.sleep(1)
    else:
        sched = BackgroundScheduler()
        sched.add_job(check_backup, "cron", hour=0, minute=1)
        sched.start()
        App().mainloop()
