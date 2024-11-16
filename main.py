import os.path
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
from platform import system

import utils

if system() != "Windows":
    tk.messagebox.showerror("不支持的系统", "此应用设计给 Windows 操作系统。")


class App(tk.ttk.Frame):
    def __init__(self, _window: tk.Tk):
        self.window = _window
        super().__init__(self.window, padding=10)
        self.grid()

        self.window.title("Clean WeChat")
        self.window.geometry("400x200")
        self.window.iconphoto(True, tk.PhotoImage(file="res/images/MaterialSymbolsMop_128x128.png"))
        self.window.resizable(False, False)

        self.account_choose = tk.ttk.Combobox(state="readonly")
        self.account_choose.grid(column=1, row=1, padx=5, pady=5, sticky="w")

        self.folder_choose = tk.ttk.Button(text="自定义文件夹", command=self.select_wx_folder)
        self.folder_choose.grid(column=2, row=1, padx=5, pady=5, sticky="w")

        self.clean_file_var = tk.BooleanVar(value=True)
        self.clean_file_checkbox = tk.ttk.Checkbutton(self.window, text="清理聊天中发送的文件",
                                                      variable=self.clean_file_var)
        self.clean_file_checkbox.grid(column=1, row=2, padx=5, pady=5, sticky="w")

        self.clean_video_var = tk.BooleanVar(value=True)
        self.clean_video_checkbox = tk.ttk.Checkbutton(self.window, text="清理聊天中的媒体（图片、媒体）",
                                                       variable=self.clean_video_var)
        self.clean_video_checkbox.grid(column=1, row=3, padx=5, pady=5, sticky="w")

        self.clean_cache_var = tk.BooleanVar(value=True)
        self.clean_cache_checkbox = tk.ttk.Checkbutton(self.window, text="清理图片缓存",
                                                       variable=self.clean_cache_var)
        self.clean_cache_checkbox.grid(column=1, row=4, padx=5, pady=5, sticky="w")

        self.clean_button = tk.ttk.Button(text="清理", command=self.clean)
        self.clean_button.grid(column=1, row=5, padx=5, pady=5, sticky="w")

        self.month_choose = tk.ttk.Combobox(values=["删除 " + str(i) + " 月以前的文件" for i in range(1, 100)],
                                            state="readonly", width=20)
        self.month_choose.current(12 - 1)
        self.month_choose.grid(column=2, row=5, padx=5, pady=5, sticky="w")

        self.send_to_trash_var = tk.BooleanVar(value=False)
        self.send_to_trash_checkbox = tk.ttk.Checkbutton(text="将文件发送到回收站", variable=self.send_to_trash_var)
        self.send_to_trash_checkbox.grid(column=2, row=2, padx=5, pady=5, sticky="w")

        self.wx_folder = ""
        self.accounts = dict()

        # noinspection PyBroadException
        try:
            self.wx_folder = self.get_wx_folder()
            self.accounts = utils.data_process.get_accounts(self.wx_folder)
            if len(self.accounts) > 0:
                self.account_choose['values'] = ["所有账户"] + list(self.accounts.keys())
                self.account_choose.current(0)
            else:
                tk.messagebox.showwarning("未找到待清理的账户", "未找到待清理的账户。")
        except OSError:
            tk.messagebox.showwarning("无法自动定位路径",
                                      "无法自动找到 WeChat Files 文件夹路径，清点击 “自定义文件夹” 按钮手动选择。")

    @staticmethod
    def get_wx_folder():
        f = os.path.join(utils.select_folder.get_win32_documents_folder_path(), "WeChat Files")
        if not os.path.exists(f): raise OSError(
            "无法获得 WeChat Files 文件夹路径：文档文件夹下不存在 WeChat Files 文件夹。")
        if not utils.select_folder.is_wechat_files_folder(f): raise OSError(
            "无法获得 WeChat Files 文件夹路径：文档文件夹下存在 WeChat Files 文件夹，但不是由微信生成。")
        return f

    def select_wx_folder(self):
        try:
            f = tk.filedialog.askdirectory(initialdir=utils.select_folder.get_win32_documents_folder_path())
        except OSError:
            f = tk.filedialog.askdirectory()
        if not f:
            tk.messagebox.showwarning("未选择文件夹", "用户取消了文件夹选择。")
            return
        if not utils.select_folder.is_wechat_files_folder(f):
            tk.messagebox.showwarning("无效文件夹", "用户选择的文件夹不是由微信生成的。")
            return
        self.wx_folder = f
        self.accounts = utils.data_process.get_accounts(self.wx_folder)
        if len(self.accounts) > 0:
            self.account_choose['values'] = ["所有账户"] + list(self.accounts.keys())
            self.account_choose.current(0)
        else:
            tk.messagebox.showwarning("未找到待清理的账户", "未找到待清理的账户。")

    def clean(self):
        if len(self.accounts) == 0:
            tk.messagebox.showwarning("未找到待清理的账户", "未找到待清理的账户。")
            return
        month_to_delete = self.month_choose.current() + 1  # 要删除多少月以前的文件
        r = tk.messagebox.askyesno("即将执行清理",
                                   f"将清理 {self.account_choose.get()} {month_to_delete} 月以前的文件，确定要继续吗？")
        if not r: return
        if self.account_choose.current() == 0:  # 获得待清理账户的路径
            paths = list(self.accounts.values())
        else:
            paths = [self.accounts[self.account_choose.get()]]
        paths = utils.data_process.gen_wx_filestorage_paths(paths)  # 获得微信账户的 File、Video、Cache 路径
        fs_list = list()  # 待清理文件夹路径
        for account_fs in paths:  # 根据用户选项选出要清理的路径
            if self.clean_file_var.get():
                fs_list.append(account_fs["file"])
            if self.clean_video_var.get():
                fs_list.append(account_fs["video"])
            if self.clean_cache_var.get():
                fs_list.append(account_fs["cache"])
        paths_to_delete = utils.data_process.gen_paths_to_delete(fs_list, month_to_delete)  # 获得待删除的文件夹路径
        utils.data_process.rm(paths_to_delete, send_to_trash=self.send_to_trash_var.get())
        tk.messagebox.showinfo("清理完成", "清理完成。")



if __name__ == "__main__":
    # noinspection PyBroadException
    try:
        window = tk.Tk()
        app = App(window)
        app.mainloop()
    except Exception as e:
        print(e)
        # noinspection PyTypeChecker
        tk.messagebox.showerror("Error", e)
