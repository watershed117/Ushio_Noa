import ctypes
from ctypes import wintypes

# 常量定义
OFN_ALLOWMULTISELECT = 0x00000200
OFN_EXPLORER = 0x00080000
OFN_NOCHANGEDIR = 0x00000008
MAX_BUFFER = 65536 * 2  # 增大缓冲区

# 定义 OPENFILENAME 结构体
class OPENFILENAME(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HANDLE),
        ("lpstrFilter", wintypes.LPCWSTR),
        ("lpstrCustomFilter", wintypes.LPWSTR),
        ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD),
        ("lpstrFile", wintypes.LPWSTR),
        ("nMaxFile", wintypes.DWORD),
        ("lpstrFileTitle", wintypes.LPWSTR),
        ("nMaxFileTitle", wintypes.DWORD),
        ("lpstrInitialDir", wintypes.LPCWSTR),
        ("lpstrTitle", wintypes.LPCWSTR),
        ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD),
        ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", wintypes.LPCWSTR),
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("pvReserved", ctypes.c_void_p),
        ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD),
    ]

# 加载 Win32 DLL
comdlg32 = ctypes.WinDLL("comdlg32.dll")
GetOpenFileNameW = comdlg32.GetOpenFileNameW
GetOpenFileNameW.argtypes = [ctypes.POINTER(OPENFILENAME)]
GetOpenFileNameW.restype = wintypes.BOOL

def open_file_dialog_multiselect(title="选择文件", file_types=None):
    """
    打开多选文件对话框，支持自定义标题和文件类型过滤器
    :param title: 对话框标题
    :param file_types: 文件类型过滤器格式 [["描述", "扩展名1", "扩展名2", ...], ...]
                      示例: [["图片", "jpg", "png"], ["所有文件", "*"]]
                      显示效果: 图片 (*.jpg, *.png) | 所有文件 (*.*)
    :return: 选择的文件路径列表
    """
    # 初始化缓冲区
    buffer = ctypes.create_unicode_buffer(MAX_BUFFER)
    
    # 配置 OPENFILENAME 结构体
    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
    ofn.nMaxFile = MAX_BUFFER
    ofn.Flags = OFN_EXPLORER | OFN_ALLOWMULTISELECT | OFN_NOCHANGEDIR
    ofn.lpstrTitle = title

    # 处理文件类型过滤器
    if file_types:
        filter_parts = []
        for type_group in file_types:
            if not isinstance(type_group, (list, tuple)) or len(type_group) < 2:
                continue

            # 提取基础描述
            base_desc = str(type_group[0]).strip()
            
            # 处理扩展名集合
            extensions = []
            for raw_ext in type_group[1:]:
                # 清理输入并标准化扩展名格式
                ext = str(raw_ext).strip().lower()
                ext = ext.replace("*", "").lstrip(".").replace(" ", "")
                
                if not ext:  # 跳过空扩展名
                    continue
                
                # 特殊处理全选类型
                if ext == "*":
                    pattern = "*.*"
                    display_ext = "*.*"
                    break  # 全选类型独占条目
                else:
                    pattern = f"*.{ext}"
                    display_ext = f".{ext}"
                
                if pattern not in extensions:
                    extensions.append((display_ext, pattern))

            else:  # 仅当未遇到break时执行（非全选类型）
                # 按扩展名字母顺序排序
                extensions.sort(key=lambda x: x[0])
                
                # 生成显示文本
                display_exts = ", ".join(e[0] for e in extensions)
                display_desc = f"{base_desc} (*{display_exts})" if display_exts else base_desc
                
                # 生成匹配模式
                patterns = ";".join(e[1] for e in extensions)
            
            # 全选类型特殊处理
            if ext == "*":
                display_desc = f"{base_desc} (*.*)"
                patterns = "*.*"

            # 添加到过滤器组件
            filter_parts.append(display_desc)
            filter_parts.append(patterns)

        if filter_parts:
            # 构建Windows API要求的过滤器格式
            filter_string = "\0".join(filter_parts) + "\0\0"
            ofn.lpstrFilter = filter_string
            ofn.nFilterIndex = 1

    # 显示对话框
    if GetOpenFileNameW(ctypes.byref(ofn)):
        # 解析缓冲区内容
        raw_buffer = buffer[:]
        parts = []
        part = []
        for c in raw_buffer:
            if c == '\0':
                if part:
                    parts.append(''.join(part))
                    part = []
                else:
                    break
            else:
                part.append(c)
        
        if not parts:
            return []
        elif len(parts) == 1:
            return [parts[0]]  # 单个文件选择
        else:
            # 多选情况：第一个元素是目录路径，后续是文件名
            directory = parts[0]
            return [directory + '\\' + file for file in parts[1:] if file]
    
    return []

# 使用示例
if __name__ == "__main__":
    selected_files = open_file_dialog_multiselect(
        title="请选择素材文件",
        file_types=[
            ["图片文件", "png", "jpeg", "jpg", "webp", "heic", "heif"],
            ["音频文件", "wav", "mp3", "aiff", "aac", "ogg", "flac"],
        ]
    )
    print("已选文件:", selected_files)