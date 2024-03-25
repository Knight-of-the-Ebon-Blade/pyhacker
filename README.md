![image](https://github.com/Knight-of-the-Ebon-Blade/pyhacker/assets/35064319/5b0c726f-d3cf-4a41-9aa3-078e58db5611)# pyhacker
向pyc中插入python代码或shellcode

使用方法：
usage: pyhacker.py [-h] [-m MODULE] [-p] [-f FILE]

pyc代码注入程序

options:
  -h, --help            show this help message and exit
  -m MODULE, --module MODULE
                        指定想要注入的模块
  -p, --python          指定注入python代码，否则注入shellcode
  -f FILE, --file FILE  注入的python代码或shellcode文件路径
