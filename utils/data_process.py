import datetime
import os
import re

from send2trash import send2trash

import utils.select_folder


def get_accounts(path: str) -> dict[str, str]:
    """获得微信所有用户的存储位置
    :param path: “WeChat Files” 文件夹路径"""
    assert utils.select_folder.is_wechat_files_folder(path)
    _l = os.listdir(path)
    result = dict()
    for account in _l:
        if account not in ("All Users", "Applet", "WMPF"):
            result[account] = os.path.join(path, account)
    return result


def need_delete(folder_name: str, month_to_delete: int = 12) -> bool:
    """检查一个文件夹是否需要删除
    :param folder_name: 检查的文件夹名称，如 “2024-09”
    :param month_to_delete: 要移除多少月以前的文件夹"""
    assert re.match("\\d{4}-\\d{2}", folder_name) is not None
    now = datetime.datetime.now()
    now_months = now.year * 12 + now.month
    # noinspection PyTypeChecker
    folder_months = int(folder_name.split("-")[0]) * 12 + int(folder_name.split("-")[1])
    return now_months - folder_months > month_to_delete


def rm(paths: list[str], send_to_trash=False):
    """递归删除文件夹。
    :param send_to_trash: 是否将文件发送至回收站
    :param paths: 要删除的文件夹列表

    :return : 删除的文件大小，单位为 B。"""

    for path in paths:
        for dirpath, dirnames, filenames in os.walk(path):
            if send_to_trash:
                try:
                    send2trash(dirpath)
                finally:
                    continue
            for filename in filenames:
                fullpath = os.path.join(dirpath, filename)
                try:
                    os.chmod(fullpath, 0x1F0FF)
                    os.remove(fullpath)
                except PermissionError:
                    continue
            try:
                os.rmdir(dirpath)
            except (PermissionError, OSError):
                continue


def gen_wx_filestorage_paths(paths: list[str]) -> list[dict[str, str]]:
    """生成微信文件存储的细分路径
    :param paths: 微信账户路径列表

    :return 含有 File、Video、Cache 路径的字典列表。"""
    result = list()
    for path in paths:
        temp = dict()
        temp['file'] = os.path.join(path, "FileStorage\\File")
        temp['video'] = os.path.join(path, "FileStorage\\Video")
        temp['cache'] = os.path.join(path, "FileStorage\\Cache")
        result.append(temp)
    return result


def gen_paths_to_delete(paths: list[str], month_to_delete: int) -> list[str]:
    """生成要删除的文件夹路径列表
    :param paths: FileStorage 细分路径列表
    :param month_to_delete: 要删除多少月以前的文件夹

    :return: 要删除的文件夹路径列表"""
    result = list()
    for path in paths:
        folders = os.listdir(path)  # 按 YYYY-MM 格式命名的文件夹列表
        for folder in folders:
            fullpath = os.path.join(path, folder)
            if (os.path.isdir(fullpath)
                    and (not re.match("\\d{4}-\\d{2}", folder) is None)
                    and need_delete(folder, month_to_delete=month_to_delete)):
                result.append(fullpath)
    return result
