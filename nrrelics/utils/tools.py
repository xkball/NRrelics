import sys
import os
import unicodedata
import difflib

# ================= 配置区域 =================

KEYS = {
    'interact': 'f',
    'sell': '3',
    'stop': 'f11',
    'exit': 'esc',
    'menu_left': 'f1',
    'up': 'up',
    'left': 'left',
    'right': 'right',
    'down': 'down'

}

FUZZY_THRESHOLD = 0.7
CORRECTION_THRESHOLD = 0.55

IGNORE_TEXTS = [
    "仅限能使用的",
    "装备时",
    "至游戏版本"
]

# ================= 工具函数 =================

def get_resource_path(relative_path):
    """ 获取资源绝对路径，兼容开发环境和打包后的 EXE 环境 """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
        return os.path.join(base_path, relative_path)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, '../../assets', relative_path)

def normalize_text(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)

    # 1. 符号统一
    text = text.replace('【', '[').replace('】', ']').replace('□', '[').replace('■', '[')

    # 2. OCR 常见错别字修复
    text = text.replace('十', '+')
    text = text.replace('陷人', '陷入')
    text = text.replace('碱', '减')
    text = text.replace('土', '+')

    # 3. [关键修复] 解决竖线被识别为数字1的问题
    # 场景： "攻击力+3|" -> OCR "攻击力+31"
    # 游戏里通常加值是个位数或双位数，+31/+21 这种如果不合理，就在这里修
    text = text.replace('+41', '+4')
    text = text.replace('+31', '+3')
    text = text.replace('+21', '+2')
    text = text.replace('+11', '+1')

    # 4. 去除空白
    text = text.replace(' ', '').replace('\t', '').replace('\r', '').replace('\n', '')
    return text

def is_fuzzy_match(ocr_line, target_line, threshold=FUZZY_THRESHOLD):
    if target_line in ocr_line: return True
    ratio = difflib.SequenceMatcher(None, ocr_line, target_line).ratio()
    return ratio >= threshold

def find_best_match_in_library(ocr_line, library):
    if not ocr_line or len(ocr_line) < 2: return None, 0.0
    best_ratio = 0.0
    best_text = None
    for item in library:
        if item == ocr_line: return item, 1.0
        ratio = difflib.SequenceMatcher(None, ocr_line, item).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_text = item
    return best_text, best_ratio
