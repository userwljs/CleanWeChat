import os
from platform import system


def get_win32_documents_folder_path():
    """获得 Windows 操作系统下的文档文件夹路径"""
    assert system() == "Windows"  # 防止开发者脑抽在 Linux 发行版上运行该函数。
    import ctypes.wintypes
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
    if not buf.value:
        raise OSError("无法获得文档文件夹路径")
    return buf.value


def is_wechat_files_folder(path: str):
    """检查是否是 WeChat Files 文件夹"""
    _l = os.listdir(path)
    return "All Users" in _l or "Applet" in _l or "WMPF" in _l
