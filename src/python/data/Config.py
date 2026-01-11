import json
import os

from src.python.ui.BackupTab import BackupTab


class Config:

    def __init__(self, config_file=os.path.join(os.environ["APPDATA"], "NRrelics","config.json")):
        self.config_file = config_file
        self._init_defaults()

    def _init_defaults(self):
        self.last_mode = "deepnight"
        self.presets_norm = [{"name": "默认预设", "items": []}]
        self.presets_deep = [{"name": "默认预设", "items": []}]
        self.bad_neg = []
        self.save_path = BackupTab.getDefaultSavePath()
        self.use_auto_backup = False

    def save(self):
        data = {
            'last_mode': self.last_mode,
            'presets_norm': self.presets_norm,
            'presets_deep': self.presets_deep,
            'bad_neg': self.bad_neg,
            'save_path': self.save_path,
            'use_auto_backup': self.use_auto_backup
        }
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding='utf-8') as f:
                    c = json.load(f)
                    self.last_mode = c.get('last_mode', self.last_mode)
                    self.presets_norm = c.get('presets_norm', self.presets_norm)
                    self.presets_deep = c.get('presets_deep', self.presets_deep)
                    self.bad_neg = c.get('bad_neg', self.bad_neg)
                    self.save_path = c.get('save_path', self.save_path)
                    self.use_auto_backup = c.get('use_auto_backup', self.use_auto_backup)
            except Exception as e:
                print(f"加载配置失败: {e}")
                self._init_defaults()
