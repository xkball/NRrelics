import PyInstaller.__main__
import sys
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建正确的文件路径
main_script = os.path.join(current_dir, 'nrrelics', 'NRrelic_bot.py')

# 构建PyInstaller命令参数
args = [
    main_script,
    '-y',
    '-F',
    '-w',
    '--add-data=assets/:.',
]

# 检查是否传入了短SHA
if len(sys.argv) > 1:
    short_sha = sys.argv[1]
    # 添加输出文件名参数，包含短SHA
    args.append(f'--name=NRrelic_bot_{short_sha}')

PyInstaller.__main__.run(args)