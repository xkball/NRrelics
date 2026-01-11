import PyInstaller.__main__

PyInstaller.__main__.run([
    'nrrelics/NRrelic_bot.py',
    '-y',
    '-F',
    '-w',
    '--add-data=assets/:.',

])