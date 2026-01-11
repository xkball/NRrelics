# NRrelic_Bot

An automated relic screening assistant based on OCR and simulated input. Designed to save your time and fingers. Based on OCR, so it only support NR in Simplified Chinese version.
## 本fork进行的修改
### 自动备份
 添加自动备份功能(默认关闭), 开启后每日00:01或者第一次启动程序时自动进行备份

 为了在启动游戏时自动检测并备份, 可以在steam的 属性/启动选项中填写如下内容,这样会先执行备份再启动游戏
```bash
    cmd /c "NRrelic_Bot.exe(改为实际路径) -check_backup && %command%"
```
### 自动SL
 添加自动SL功能(默认关闭), 开启后如果卢恩低于阈值,并且出货量低于阈值,会自动执行SL操作

 其实是半自动, 会退出游戏并自动替换存档, 需要手动重进进入游戏并重新开始挂机

### 对原程序的修改
 去除了原来的校验鼠标位置操作, 改为在配置文件自定义区域, 默认配置文件使用在屏幕上两个点的相对位置定义一个方框作为ROI, 针对2560x1440屏幕经过测试可以正常使用

 配置文件位置现在固定在`%AppData%\Roaming\NRrelic_Bot\config.json`

 roi配置里如果填写0-1小数, 代表屏幕上相对位置, 大于一整数代表绝对位置, 请不要混用

 未进行多显示器适配, 游戏必须在主显示器上
## Disclaimer (Must Read)

This software operates solely on **Optical Character Recognition (OCR)** and **simulated mouse/keyboard clicks**. It **does not** read or modify any game memory.

* **Safety**: While theoretically safe, using automation scripts in online environments always carries risk.
* **Recommendation**: **Strongly recommended for use in Offline Mode or with EAC (Easy Anti-Cheat) disabled.**
* **Liability**: This tool is for educational purposes only. The author is not responsible for any bans resulting from online use.
* **Fair Play**: Not intended for malicious Save-Load (SL) exploits.

## Features

* **Auto-Recognition**: Automatically identifies relic attributes using OCR.
* **Dual Modes**: Supports both "Normal" and "Deepnight" relic modes.
* **Smart Filtering**:
    * **Custom Presets**: Define multiple desired attribute combinations (e.g., "Phys Atk + HP" for melee, "Magic Atk + Crit" for mages).
    * **Logic**: If a relic matches 2 or more attributes from *any* active preset, it is **kept**. Otherwise, it is automatically **sold**.
* **Blacklist System**: Automatically detects and sells relics with "fatal" negative attributes (e.g., "HP Drain") defined in your blacklist.

## How to Use

1.  **Launch**:
    * Open the game and stand in front of the **Pot Merchant** or the **Collector** interface.
    * Run `NRrelic_Bot.exe`.
2.  **Configure**:
    * Select your mode (Normal/Deepnight).
    * Add your desired attribute presets in the software.
3.  **Start AFK**:
    * In the game, aim your crosshair/cursor at the item you want to purchase.
    * Click the **Start** button on the bot.
    * The bot will automatically loop: `Buy -> Scan -> Keep/Sell`.

### Key Mappings
The software uses the default game keybinds:
* **Interact (Buy/Confirm)**: `F`
* **Sell**: `3`
* **Stop/Pause Bot**: `F11`

---

## Acknowledgments

* **Data Source**: The relic attribute list used in this project is referenced from the guide by Bilibili content creator **Cinderella小辛**.
