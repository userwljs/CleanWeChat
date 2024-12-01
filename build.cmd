@echo off
python -m nuitka --standalone ^
                 --remove-output ^
                 --windows-console-mode="attach" ^
                 --enable-plugins="tk-inter" ^
                 --output-filename="Clean_WeChat.exe" ^
                 --main="main.py" ^
                 --windows-icon-from-ico="res/images/MaterialSymbolsMop_128x128.ico" ^
                 --include-data-dir=res=res