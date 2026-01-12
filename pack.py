import PyInstaller.__main__
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(current_dir, 'nrrelics', 'NRrelic_bot.py')

args = [
    main_script,
    '-y',
    '-F',
    '-w',
    '--add-data=assets/:.',
    '--collect-all=onnxruntime',
    '--collect-all=rapidocr_onnxruntime',
    '--copy-metadata=onnxruntime',
    '--copy-metadata=rapidocr_onnxruntime',
]

if len(sys.argv) > 1:
    short_sha = sys.argv[1]
    output_file = os.environ.get("GITHUB_OUTPUT")
    print(short_sha,output_file)
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"artifact_name=NRrelic_bot_NightlyBuild_{short_sha}")

PyInstaller.__main__.run(args)