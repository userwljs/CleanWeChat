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
        months = self.month_choose.current() + 1  # 要删除多少月以前的文件
        r = tk.messagebox.askyesno("即将执行清理",
                                   f"将清理 {self.account_choose.get()} {months} 月以前的文件，确定要继续吗？")
        if not r: return
        if self.account_choose.current() == 0:
            paths = list(self.accounts.values())
        else:
            paths = [self.accounts[self.account_choose.get()]]
        paths = self.gen_paths(paths)
        paths = self.gen_paths_to_delete(paths, month_to_delete=months)
        size = 0
        for path in paths:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    fullpath = os.path.join(dirpath, filename)
                    size += os.path.getsize(fullpath)
                    try:
                        os.chmod(fullpath, 0x1F0FF)
                        os.remove(fullpath)
                    except PermissionError:
                        size -= os.path.getsize(fullpath)
        tk.messagebox.showinfo("清理完成", f"清理完成，清理了 {self.hum_convert(size)}")

    @staticmethod
    def hum_convert(value):
        units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return "%.2f %s" % (value, units[i])
            value = value / size

    def gen_paths(self, paths: list[str]):
        result = list()
        for path in paths:
            if self.clean_file_var.get():
                result.append(os.path.join(path, "FileStorage\\File"))
            if self.clean_video_var.get():
                result.append(os.path.join(path, "FileStorage\\Video"))
            if self.clean_cache_var.get():
                result.append(os.path.join(path, "FileStorage\\Cache"))
        return result

    @staticmethod
    def gen_paths_to_delete(paths: list[str], month_to_delete=12):
        result = list()
        for path in paths:
            result += utils.data_process.get_folders_to_delete(path, month_to_delete=month_to_delete)
        return result


if __name__ == "__main__":
    window = tk.Tk()
    app = App(window)
    app.mainloop()
