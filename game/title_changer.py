import ctypes
from ctypes import wintypes

# 定义需要的Windows API函数
user32 = ctypes.WinDLL('user32', use_last_error=True)

# 定义需要的Windows API函数和常量
SetWindowText = user32.SetWindowTextW
SetWindowText.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
SetWindowText.restype = wintypes.BOOL

FindWindow = user32.FindWindowW
FindWindow.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
FindWindow.restype = wintypes.HWND

def get_hwnd(window_name:str)->int:
    return FindWindow(None, window_name)

# 修改窗口标题
def set_window_title(hwnd:int, new_title):
    # 设置新标题
    if SetWindowText(hwnd, new_title):
        print(f"窗口标题已更新为: {new_title}")
        return True
    else:
        print(f"无法更新窗口标题，错误代码: {ctypes.get_last_error()},hwnd:{hwnd}")
        return False
