import datetime
import os
import re

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


def get_folders_to_delete(path: str, month_to_delete: int = 12) -> list[str]:
    """给定一个微信存储的路径，返回一个包含路径的列表。
    :param path: 微信存储文件夹的路径，如 “D:\\User\\Documents\\WeChat Files\\wxid_\\FileStorage\\File”
    :param month_to_delete: 要移除多少月以前的文件夹
    """
    _l = os.listdir(path)
    result = list()
    for f in _l:
        if not re.match("\\d{4}-\\d{2}", f) is None:
            if need_delete(f, month_to_delete=month_to_delete):
                result.append(os.path.join(path, f))
    return result
