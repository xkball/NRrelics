import os
from nrrelics.utils.tools import normalize_text, get_resource_path

class DataLoader:
    @staticmethod
    def load_txt(filename):
        real_path = get_resource_path(filename)

        if not os.path.exists(real_path):
            print(f"警告: 找不到文件 {real_path}")
            return []

        with open(real_path, 'r', encoding='utf-8') as f:
            lines = set()
            for line in f.readlines():
                clean = normalize_text(line)
                if clean: lines.add(clean)
            return sorted(list(lines))

    @staticmethod
    def get_data():
        return (DataLoader.load_txt("data/normal.txt"),
                DataLoader.load_txt("data/deepnight_pos.txt"),
                DataLoader.load_txt("data/deepnight_neg.txt"))

    @staticmethod
    def get_master_library():
        n = DataLoader.load_txt("data/normal.txt")
        dp = DataLoader.load_txt("data/deepnight_pos.txt")
        dn = DataLoader.load_txt("data/deepnight_neg.txt")
        return sorted(list(set(n + dp + dn)))
