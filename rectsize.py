import win32gui
import win32ui
import win32api
import win32con
import time

def is_left_down():
    return win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0

def get_mouse_pos():
    return win32api.GetCursorPos()

time.sleep(1)

hwnd = win32gui.GetDesktopWindow()
hdc = win32gui.GetWindowDC(hwnd)
dc = win32ui.CreateDCFromHandle(hdc)
screen_w = win32api.GetSystemMetrics(0)
screen_h = win32api.GetSystemMetrics(1)

pen = win32ui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(255, 0, 0))
dc.SelectObject(pen)

print("按住鼠标左键拖动选择区域...")

while not is_left_down():
    pass

start = get_mouse_pos()
last_rect = None

while is_left_down():
    cur = get_mouse_pos()

    if last_rect:
        dc.DrawFocusRect(last_rect)

    rect = (start[0], start[1], cur[0], cur[1])
    dc.DrawFocusRect(rect)
    last_rect = rect

dc.DrawFocusRect(last_rect)

end = get_mouse_pos()

x1 = min(start[0], end[0])
y1 = min(start[1], end[1])
x2 = max(start[0], end[0])
y2 = max(start[1], end[1])

print("\n选中区域：")
print(f"左上角: ({x1}, {y1})")
print(f"右下角: ({x2}, {y2})")
print(f"宽: {x2 - x1}, 高: {y2 - y1}")
rx1 = x1 / screen_w
ry1 = y1 / screen_h
rx2 = x2 / screen_w
ry2 = y2 / screen_h
print(f"{rx1:.4f}, {ry1:.4f}, {rx2:.4f}, {ry2:.4f}")

win32gui.ReleaseDC(hwnd, hdc)