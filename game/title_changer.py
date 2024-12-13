import ctypes
from ctypes import wintypes

# 定义需要的Windows API函数
user32 = ctypes.WinDLL('user32', use_last_error=True)

# 定义需要的Windows API函数和常量
SetWindowText = user32.SetWindowTextW
SetWindowText.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
SetWindowText.restype = wintypes.BOOL

# FindWindow = user32.FindWindowW
# FindWindow.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
# FindWindow.restype = wintypes.HWND

# def get_hwnd(window_name:str)->int:
#     return FindWindow(None, window_name)

# 修改窗口标题
def set_window_title(hwnd:int, new_title):
    # 设置新标题
    if SetWindowText(hwnd, new_title):
        print(f"窗口标题已更新为: {new_title}")
        return True
    else:
        print(f"无法更新窗口标题，错误代码: {ctypes.get_last_error()},hwnd:{hwnd}")
        return False


# 定义需要的Windows API函数原型
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

# 获取当前进程ID
current_pid = ctypes.windll.kernel32.GetCurrentProcessId()

# 定义一个列表用于存储窗口句柄
window_handles = []

# 定义回调函数，用于枚举窗口
def foreach_window(hwnd, lParam):
    if IsWindowVisible(hwnd):
        pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == current_pid:
            # 找到当前进程的窗口句柄，将其添加到列表中
            window_handles.append(hwnd)  # 收集窗口句柄
    return True  # 继续枚举

# 转换回调函数为ctypes可用的形式
enum_proc = EnumWindowsProc(foreach_window)

def get_all_current_process_window_handles():
    global window_handles
    window_handles.clear()  # 清空之前存储的窗口句柄
    EnumWindows(enum_proc, 0)  # 枚举所有窗口
    return window_handles  # 返回所有窗口句柄

# # 读取JSON文件函数
# def read_json(file_path:str):
#     """
#     读取指定路径的JSON文件，并返回数据。
    
#     参数:
#     file_path: JSON文件的路径。
    
#     返回:
#     数据字典。
#     """
#     with open(file_path, 'r', encoding='utf-8') as file:
#         data = json.load(file)
#     return data

# # 存储数据到JSON文件函数
# def save_to_json(data:dict, file_path:str):
#     """
#     将数据保存到指定的JSON文件。
    
#     参数:
#     data: 要保存的数据，可以是字典或列表。
#     file_path: 要保存的JSON文件路径。
#     """
#     with open(file_path, 'w', encoding='utf-8') as file:
#         json.dump(data, file, ensure_ascii=False, indent=4)



