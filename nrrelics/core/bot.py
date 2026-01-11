import datetime
import os
import time

import cv2
import mss
import numpy as np
import pydirectinput
from rapidocr_onnxruntime import RapidOCR

from nrrelics.core.ProportionROI import ProportionROI
from nrrelics.data.Config import Config
from nrrelics.data.loader import DataLoader
from nrrelics.ui.BackupTab import BackupTab
from nrrelics.utils.tools import KEYS, CORRECTION_THRESHOLD, normalize_text, find_best_match_in_library


class BotLogic:
    def __init__(self, log_func, config : Config):
        self.log = log_func
        self.config = config
        self.should_stop = False
        self.master_library = DataLoader.get_master_library()
        self.keep_count = 0
        if not os.path.exists("logs"): os.makedirs("logs")
        try:
            self.ocr = RapidOCR()
            self.log("OCR 引擎初始化成功")
        except:
            self.log("错误: OCR 初始化失败")

    def press(self, key, duration=0.03, wait=0.05):
        if self.should_stop: return
        pydirectinput.keyDown(key)
        time.sleep(duration)
        pydirectinput.keyUp(key)
        time.sleep(wait)

    def get_screen_image(self, roi: ProportionROI = ProportionROI(0.3, 0.2, 0.7, 0.8)):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            roi_ = roi.getROI(monitor)
            img = np.array(sct.grab(roi_))
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def extract_text_by_color(self, img):
        # [保留图片留证功能]
        ts = datetime.datetime.now().strftime("%H_%M_%S_%f")
        # cv2.imwrite(f"logs/{ts}_1_raw.jpg", img) # 可选：写入硬盘

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        kernel = np.ones((2, 2), np.uint8)
        mask_blue = cv2.dilate(mask_blue, kernel, iterations=1)
        mask_white = cv2.bitwise_not(mask_blue)

        img_neg = cv2.bitwise_and(img, img, mask=mask_blue)
        _, img_neg_bin = cv2.threshold(cv2.cvtColor(img_neg, cv2.COLOR_BGR2GRAY), 10, 255, cv2.THRESH_BINARY)
        img_pos = cv2.bitwise_and(img, img, mask=mask_white)
        _, img_pos_bin = cv2.threshold(cv2.cvtColor(img_pos, cv2.COLOR_BGR2GRAY), 50, 255, cv2.THRESH_BINARY)

        # cv2.imwrite(f"logs/{ts}_2_pos.jpg", img_pos_bin)
        # cv2.imwrite(f"logs/{ts}_3_neg.jpg", img_neg_bin)

        res_neg, _ = self.ocr(img_neg_bin)
        res_pos, _ = self.ocr(img_pos_bin)

        list_neg = [normalize_text(line[1]) for line in res_neg] if res_neg else []
        list_pos = [normalize_text(line[1]) for line in res_pos] if res_pos else []
        return list_pos, list_neg

    def wait_for_result_screen(self, timeout=2.5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.should_stop: return False, None
            img = self.get_screen_image()
            res, _ = self.ocr(img)
            text = "".join([line[1] for line in res]) if res else ""
            if "情景" in text or "卖出" in text or "关闭" in text:
                return True, img
            time.sleep(0.05)
        return False, None

    def purchase_loop(self, config):
        self.press(KEYS['interact'])
        self.press(KEYS['interact'])
        time.sleep(0.15)
        self.press(KEYS['interact'])

        success, img = self.wait_for_result_screen(timeout=2.5)

        if not success:
            self.press(KEYS['interact'])
            return

        keep, reason, debug_info = self.check_logic(img, config)

        if keep:
            self.keep_count += 1
            self.log(f"√ 保留 | {reason}")
            self.press(KEYS['interact'])
        else:
            self.log(f"× 卖出 | {reason}")
            print(f"\n--- 卖出详情 ---{debug_info}\n----------------")
            self.press(KEYS['sell'], duration=0.15, wait=0.2)
            self.press(KEYS['interact'], duration=0.1, wait=0.2)

    def check_logic(self, img, config):
        mode = config['mode']
        active_presets = config['presets']
        bad_neg_list = config['bad_neg']

        pos_lines, neg_lines = self.extract_text_by_color(img)

        print("\n" + "=" * 40)
        print(f"[OCR 原始识别结果]")
        print(f"负面池 (蓝字): {neg_lines}")
        print(f"正面池 (白字): {pos_lines}")
        print("-" * 40)

        # 1. 负面检查 (带纠错 + 全等匹配)
        if mode == "deepnight":
            print(f"[负面检查] 开始比对黑名单...")
            for ocr_line in neg_lines:
                corrected, score = find_best_match_in_library(ocr_line, self.master_library)
                target = corrected if score > CORRECTION_THRESHOLD else ocr_line

                for bad in bad_neg_list:
                    # 负面依然建议用“包含”逻辑，因为负面词条往往是句子的一部分
                    if bad in target:
                        msg = f"致命负面 [{bad}] (来源: {ocr_line} -> {target})"
                        return False, msg, f"{msg}"
            print(f"负面检查通过")

        # 2. 正面标准化
        print(f"[正面标准化] 开始全库纠错...")
        normalized_pos_lines = []
        for ocr_line in pos_lines:
            if len(ocr_line) < 2: continue
            if "情景" in ocr_line: continue  # 跳标题

            corrected, score = find_best_match_in_library(ocr_line, self.master_library)
            if score > CORRECTION_THRESHOLD:
                normalized_pos_lines.append(corrected)
                print(f"'{ocr_line}' -> 修正为: '{corrected}' ({score:.2f})")
            else:
                print(f"'{ocr_line}' -> 无法识别/噪点")

        # 3. 遍历预设 (精确匹配)
        print(f"[预设匹配] 开始匹配 {len(active_presets)} 套方案...")

        for preset in active_presets:
            preset_name = preset['name']
            wanted_items = preset['items']
            match_count = 0
            hits = []

            for line in normalized_pos_lines:
                for wanted in wanted_items:
                    # [核心修改] 必须完全相等才算命中 (避免包含关系误判)
                    if wanted == line:
                        match_count += 1
                        hits.append(wanted)
                        break

            if match_count >= 2:
                success_msg = f"命中方案[{preset_name}]: {hits}"
                print(f"判定保留! {success_msg}")
                return True, success_msg, ""
            else:
                print(f"预设[{preset_name}] 不满足: {match_count}/2 {hits}")

        return False, "不符合任何启用预设", "不满足条件"

    def getRune(self) -> int:
        img = self.get_screen_image(ProportionROI(0.2578, 0.1, 0.3125, 0.131))
        res, _ = self.ocr(img)
        if not res:
            pass
        for line in res:
            print(line)

    def exitToGameMenu(self):
        self.press(KEYS['exit'], wait= 0.2)
        self.press(KEYS['exit'], wait= 0.2)
        self.press(KEYS['menu_left'], wait= 0.2)
        self.press(KEYS['up'], wait= 0.2)
        self.press(KEYS['interact'], wait=0.2)
        self.press(KEYS['interact'], wait=0.2)
        self.press(KEYS['left'], wait=0.2)
        self.press(KEYS['interact'], wait=0.2)

    def run(self, config):
        self.log(">>> 请在3秒内聚集游戏窗口")
        time.sleep(3)
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            roi = self.config.buy_roi
            if config["mode"] == "deepnight":
                roi = self.config.buy_deepnight_roi
            pydirectinput.moveTo(roi.getCenter(monitor))
        self.log(">>> 开始循环...")
        loopCount = 0
        while not self.should_stop:
            loopCount += 1
            if loopCount % 20 == 0 and self.config.use_auto_sl:
                rune = self.getRune()
                if 0 < rune < self.config.sl_threshold:
                    self.log(f"卢恩低于阈值 ({rune}/{self.config.sl_threshold})，执行自动SL.")
                    if self.keep_count >= self.config.keep_count_threshold:
                        self.log("出货量达标, 自动停止")
                        break
                    else:
                        self.exitToGameMenu()
                        time.sleep(10)
                        BackupTab.runRestoreStatic(self.config.save_path, self.config.sl_save_path)
            self.purchase_loop(config)
            time.sleep(0.1)
