import json
import os

from nrrelics.core.ProportionROI import ProportionROI
from nrrelics.ui.BackupTab import BackupTab


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
        self.use_auto_sl = False
        self.sl_save_path = ""
        self.sl_threshold = 100000
        self.keep_count_threshold = 10
        self.stone_roi = ProportionROI(0.3, 0.5, 0.7, 0.8)
        self.rune_roi = ProportionROI(0.2578, 0.1, 0.3125, 0.131)
        self.buy_roi = ProportionROI(0.0465, 0.7757, 0.0996, 0.8701)
        self.buy_deepnight_roi = ProportionROI(0.1660, 0.7771, 0.2195, 0.8701)

    def save(self):
        data = {
            'last_mode': self.last_mode,
            'presets_norm': self.presets_norm,
            'presets_deep': self.presets_deep,
            'bad_neg': self.bad_neg,
            'save_path': self.save_path,
            'use_auto_backup': self.use_auto_backup,
            'use_auto_sl': self.use_auto_sl,
            'sl_save_path': self.sl_save_path,
            'sl_threshold': self.sl_threshold,
            'keep_count_threshold': self.keep_count_threshold,
            'stone_roi': self.stone_roi.to_dict(),
            'rune_roi': self.rune_roi.to_dict(),
            'buy_roi': self.buy_roi.to_dict(),
            'buy_deepnight_roi': self.buy_deepnight_roi.to_dict(),
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
                    self.use_auto_sl = c.get('use_auto_sl', self.use_auto_sl)
                    self.sl_save_path = c.get('sl_save_path', self.sl_save_path)
                    self.sl_threshold = c.get('sl_threshold', self.sl_threshold)
                    self.keep_count_threshold = c.get('keep_count_threshold', self.keep_count_threshold)
                    self.stone_roi = ProportionROI(**c.get('stone_roi', self.stone_roi.__dict__))
                    self.rune_roi = ProportionROI(**c.get('rune_roi', self.rune_roi.__dict__))
                    self.buy_roi = ProportionROI(**c.get('buy_roi', self.buy_roi.__dict__))
                    self.buy_deepnight_roi = ProportionROI(**c.get('buy_deepnight_roi', self.buy_deepnight_roi.__dict__))
            except Exception as e:
                print(f"加载配置失败: {e}")
                self._init_defaults()
