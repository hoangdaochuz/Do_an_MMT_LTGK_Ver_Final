import socket
# from tkinter.filedialog import asksaveasfilename
# from PIL import Image
import pyautogui
import wmi
import tkinter as tk
import tkinter.messagebox
# import threading
import struct
import os
import winreg
import datetime


# --- functions ---
#--------------------- bắt đầu chụp màn hình ---------------------
def take_screenshot():  # PEP8: verb as function name

    screenshot = pyautogui.screenshot()  # PEP8: `lower_case_names` for variables
    # PEP8: spaces around `=`

    # using `asksaveasfilename()` (or any other GUI elements) on server is useless - user can't see GUI from server
    # path = asksaveasfilename()
    # path = path + "_capture1.png"
    path = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f_capture.png')
    screenshot.save(path)

    return path
# ----------------------Kết thúc chụp màn hình -----------------------


# --------------------- Bắt đầu process -----------------
def Process(conn):
    while True:
        data = conn.recv(1024).decode("utf8")
        if data == "XEM":
            f = wmi.WMI()
            arr = []
            for process in f.Win32_Process():
                pair = f"{process.ProcessId}    {process.Name}   {process.Threadcount}"
                conn.sendall(bytes(pair, "utf8"))

            conn.sendall(bytes("done", "utf8"))
        elif data == "KILL":
            name_app_kill = conn.recv(1024).decode("utf8")
            result = os.system(f'taskkill /PID ' + name_app_kill + '.exe /F')
            if result == 0:
                tkinter.messagebox.showinfo(title="Notification", message="Da diet process")
            else:
                tkinter.messagebox.showerror(title="ERROR", message="ERROR: Not found")
        elif data == "START":
            name_app_start = conn.recv(1024).decode("utf8")
            os.system("start " + name_app_start + ".exe")
        elif data == "Exit":
            break
    return
# ------------------ Kết thúc Process ----------------------


# ------------------ Bắt đầu registry ----------------------
def splitPath(path):
    if isinstance(path, str):
        mark = 0
        key = ""
        subkey = ""
        for i in range(len(path)):
            if path[i] == "\\":
                mark = i
                break
            else:
                mark = len(path)

        for h in range(mark):
            key += path[h]
        for j in range(mark + 1, len(path)):
            subkey += path[j]
    return key, subkey


def createKey(conn, new_key, subkey, keyCre):
    try:
        aReg = winreg.ConnectRegistry(None, new_key)
        aKey = winreg.OpenKey(aReg, subkey)
        winreg.CreateKey(aKey, keyCre)
        msg = "Tạo key thành công"
        print(msg)
        conn.sendall(bytes(msg, "utf-8"))
    except Exception as e:
        print(e)
        msg = "Lỗi"
        conn.sendall(bytes(msg, "utf-8"))


def getValue(path, name, start_key=None):
    try:
        if isinstance(path, str):
            path = path.split("\\")
        if start_key is None:
            start_key = getattr(winreg, path[0])
            return getValue(path[1:], name, start_key)
        else:
            subkey = path.pop(0)
        with winreg.OpenKey(start_key, subkey) as handle:
            assert handle
            if path:
                return getValue(path, name, handle)
            else:
                desc, i = None, 0
                while not desc or desc[0] != name:
                    desc = winreg.EnumValue(handle, i)
                    i += 1
                return desc[1]
    except Exception as e:
        return "Lỗi"


def setValue(conn, key, subkey, nameValue, value, typeValue):
    try:
        KPW = winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(KPW, nameValue, 0, typeValue, value)
        msg = "Set value thành công"
        conn.send(bytes(msg, "utf-8"))
    except Exception as e:
        print(e)
        msg = "Lỗi"
        conn.send(bytes(msg, "utf-8"))


def deleteKey(conn, new_key, subkey):
    try:
        winreg.DeleteKey(new_key, subkey)
        msg = "Xóa key thành công"
        print(msg)
        conn.sendall(bytes(msg, "utf-8"))
    except Exception as e:
        print(e)
        msg = "Lỗi"
        conn.sendall(bytes(msg, "utf-8"))


def deleteValue(conn, new_key, subkey, nameValue):
    try:
        KPW = winreg.OpenKey(new_key, subkey, 0, winreg.KEY_WRITE)
        winreg.DeleteValue(KPW, nameValue)
        msg = "Delete value thành công"
        conn.sendall(bytes(msg, "utf-8"))
    except Exception as e:
        print(e)
        msg = "Lỗi"
        conn.sendall(bytes(msg, "utf-8"))


def HKey_Constants(key):
    global checkKey
    global checkProc
    checkproc = 0

    if key == "HKEY_CURRENT_USER":
        checkproc = 1
        checkKey = winreg.HKEY_CURRENT_USER
    if key == "HKEY_CLASSIES_ROOT":
        checkproc = 1
        checkKey = winreg.HKEY_CLASSES_ROOT
    if key == "HKEY_LOCAL_MACHINE":
        checkproc = 1
        checkKey = winreg.HKEY_LOCAL_MACHINE
    if key == "HKEY_USERS":
        checkproc = 1
        checkKey = winreg.HKEY_USERS
    if key == "HKEY_CURRENT_CONFIG":
        checkproc = 1
        checkKey = winreg.HKEY_CURRENT_CONFIG

    if checkproc == 0:
        checkKey = "Lỗi"
    return checkKey


def checkTypeValue(typeVa):
    global TypeValue

    if typeVa == "String":
        TypeValue = winreg.REG_SZ
    elif typeVa == "Binary":
        TypeValue = winreg.REG_BINARY
    elif typeVa == "DWORD":
        TypeValue = winreg.REG_DWORD
    elif typeVa == "QWORD":
        TypeValue = winreg.REG_QWORD
    elif typeVa == "Multi-string":
        TypeValue = winreg.REG_MULTI_SZ
    elif typeVa == "Expand string":
        TypeValue = winreg.REG_EXPAND_SZ

    return TypeValue


def Registry(conn, addr):
    # Lấy option của người dùng
    while True:
        data = conn.recv(1024).decode("utf-8")

        if data != "quit_registry":
            # Tách nguyên chuỗi data client gửi
            if isinstance(data, str):
                data = data.split("$")

            # Option do client chọn
            opt = data[0]
            # Tách path client vừa nhập để lấy key và subkey
            path = data[1]
            key, subkey = splitPath(path)

            if HKey_Constants(key) != "Lỗi":
                global new_key
                new_key = HKey_Constants(key)

                # Thực hiện từng chức năng client yêu cầu
                if opt == "Create key":
                    keyCre = data[2]
                    createKey(conn, new_key, subkey, keyCre)

                elif opt == "Set value":
                    nameValue = data[2]
                    valued = data[3]
                    TypeVal = data[4]

                    new_TypeVal = checkTypeValue(TypeVal)
                    setValue(conn, new_key, subkey, nameValue, valued, new_TypeVal)

                elif opt == "Delete key":
                    deleteKey(conn, new_key, subkey)

                elif opt == "Delete value":
                    nameValue = data[2]
                    deleteValue(conn, new_key, subkey, nameValue)

                elif opt == "Get value":
                    nameValue = data[2]
                    valued = getValue(path, nameValue)
                    msg = "Get value thành công"
                    conn.sendall(bytes(msg, "utf-8"))
                    conn.sendall(bytes(valued, "utf-8"))
            else:
                msg = "Lỗi"
                conn.sendall(bytes(msg, "utf-8"))
        if data == "quit_registry":
            break
    return
# ------------------ Kết thúc registry ---------------------


def handle_client(conn, addr):
    while True:
        print('[handle_client] read command')
        command = conn.recv(1024).decode("utf8")
        command = command.lower()

        print('[handle_client] run command:', command)

        if command == "takepic":
            print('[handle_client] take screenshot')
            path = take_screenshot()

            # displaying on serer make no sense because user can't see it.
            # im = Image.open(path)
            # im.show()

            file_size = os.stat(path).st_size
            print('[handle_client] file size:', file_size)
            file_size = struct.pack('>I', file_size)  # convert `integer` to `4 bytes`
            conn.send(file_size)

            print('[handle_client] open file')
            file_handler = open(path, 'rb')

            total_size = 0
            while True:
                print('[handle_client] read data chunk from file')
                data_chunk = file_handler.read(2048)

                size = len(data_chunk)
                if not data_chunk:
                    break

                total_size += size
                print('[handle_client] send data chunk:', size, 'total:', total_size)
                conn.send(data_chunk)

            print('[handle_client] close file')
            file_handler.close()

        elif command == "app running":
            Process(conn)
        elif command == "registry":
            Registry(conn, addr)
        elif command == "quit":
            conn.close()
            break


# --- main ---
root = tk.Tk()
root.withdraw()
HOST = ''  # PEP8: spaces around `=`
PORT = 65432  # PEP8: spaces around `=`

print('Starting ...')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # PEP8: space after `,`
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # solution for "[Error 89] Address already in use". Use before bind()
s.bind((HOST, PORT))
s.listen()

# all_threads = []
all_clients = []

try:
    while True:
        print('Waiting for client')
        conn, addr = s.accept()

        print('Handle client')

        # run in current thread - only one client can connect
        handle_client(conn, addr)
        all_clients.append((conn, addr))

        # run in separated thread - many clients can connect
        # t = threading.Thread(taget=handle_client, args=(conn, addr))
        # t.start()
        # all_threads.append(t)
except KeyboardInterrupt:
    print('Stopped by Ctrl+C')
finally:
    s.close()
    # for t in all_threads:
    #    t.join()
    for conn, addr in all_clients:
        conn.close()