# Cái điều khiển đó thì sau sửa lại. Cái đầu tiên vào là menu. Sau khi kích vào menu thì nó mới là câu lệnh bình thường
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
import tkinter.messagebox
from PIL import Image
import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# -------------func-------------

def ConnectToServer():
    HOST = entry.get()
    PORT = 65432
    test = True
    try:
        s.connect((HOST, PORT))
    except Exception as e:
        tkinter.messagebox.showerror(title="Lỗi", message="Lỗi kết nối đến server")
        test = False
    if test:
        tkinter.messagebox.showinfo(title="Thông báo", message="Đã kết nối tới server thành công")

#============================ Chụp màn hình===========================

def takeScreen():
    msg = "TAKEPIC"
    print('[take_screen] send command:', msg)
    s.sendall(msg.encode())
    file_size = s.recv(4)
    file_size = struct.unpack('>I', file_size)[0]  # convert `4 bytes` to `integer`
    return file_size
def save_img():
    file_size = takeScreen()
    path=asksaveasfilename()
    file_handler = open(path, "wb")
    total_size = 0
    while total_size < file_size:
        data_chunk = s.recv(2048)
        size = len(data_chunk)
        total_size += size
        file_handler.write(data_chunk)
    file_handler.close()
    tkinter.messagebox.showinfo(title="Success", message="Downloaded Successfully")
    im = Image.open(path)
    im.show()
def w_takeScreen():
    w_child = Toplevel(root)
    w_child.title("Screenshot")
    w_child.geometry("200x100")
    #add Button
    button_save = tk.Button(w_child,text="Save", command= lambda : save_img())
    button_save.grid(row=1, column=1)

# ========================Kết thúc chụp màn hình==========================


# ==========================Processing====================================
def Start(entry1):
    app_start = entry1.get()
    s.sendall(bytes(app_start, "utf8"))


def w_Start():
    msg = "START"
    s.sendall(bytes(msg, "utf8"))
    w_c_start = Toplevel(root)
    entry1 = tk.Entry(w_c_start, width=30)
    entry1.insert(0, 'Nhập tên app(vd: notepad,...)')
    w_c_start.geometry("300x200")
    w_c_start.title("start")
    entry1.grid(row=2, column=1)
    button = tk.Button(w_c_start, text="OK", command=lambda: Start(entry1))
    button.grid(row=3, column=1)


def Kill(entry1):
    app_Kill = entry1.get()
    s.sendall(bytes(app_Kill, "utf8"))


def w_Kill():
    msg = "KILL"
    s.sendall(bytes(msg, "utf8"))
    w_c_kill = Toplevel(root)
    entry1 = tk.Entry(w_c_kill, width=30)
    entry1.insert(0, 'Nhập tên app(vd: notepad,...)')
    w_c_kill.geometry("300x200")
    w_c_kill.title("kill")
    entry1.grid(row=2, column=1)
    button = tk.Button(w_c_kill, text="OK", command=lambda: Kill(entry1))
    button.grid(row=3, column=1)


def w_Xem(my_w_child,tree):
    msg = "XEM"
    s.sendall(bytes(msg, "utf8"))

    # w_c_Xem = Toplevel(root)
    # w_c_Xem.geometry("650x300")
    # w_c_Xem.title("Xem")
    # columns = ('Id Process', 'Name process', 'Count threading')
    #================
    # tree = ttk.Treeview(w_c_Xem, columns=columns)
    # tree = ttk.Treeview(my_w_child, columns=columns)

    # define headings
    tree.heading('#0', text='Item')
    tree.heading('#1', text='Id Process')
    tree.heading('#2', text='Name process')
    tree.heading('#3', text='Count threading')

    # Specify attributes of the columns
    tree.column('#0', stretch=tk.YES)
    tree.column('#1', stretch=tk.YES)
    tree.column('#2', stretch=tk.YES)
    tree.column('#3', stretch=tk.YES)

    tree.grid(row=5, columnspan=4, sticky='nsew')
    # generate sample data
    list_process = []
    i = 0
    list_process.clear()
    while True:
        recv_proc = s.recv(1024).decode("utf8")
        if recv_proc == "done":
            break
        list_process.append(recv_proc)
    for item in list_process:
        tree.insert(parent='', index='end', text="Item_" + str(i), values=(item))
        i=i+1
def Xoa_table(tree):
    for i in tree.get_children():
        tree.delete(i)

def Exit(my_w_child):
    msg = "Exit"
    s.sendall(bytes(msg, "utf8"))
    my_w_child.destroy()


def my_open():
    columns = ('Id Process', 'Name process', 'Count threading')
    msg = "app running"
    s.sendall(bytes(msg, "utf8"))
    my_w_child = Toplevel(root)
    my_w_child.geometry("1200x300")
    my_w_child.title("Process running")
    tree = ttk.Treeview(my_w_child, columns=columns)
    # add button
    myButton_Start = tk.Button(my_w_child, text="START", command=lambda: w_Start(), font=10)
    myButton_Start.grid(row=1, column=1)
    myButton_Kill = tk.Button(my_w_child, text="KILL", command=lambda: w_Kill(), font=10)
    myButton_Kill.grid(row=1, column=2)
    myButton_Xem = tk.Button(my_w_child, text="See Processing", command=lambda:  w_Xem(my_w_child,tree), font=10)
    myButton_Xem.grid(row=1, column=3)
    myButton_Xoa_table= tk.Button(my_w_child,text="Clear table",command=lambda : Xoa_table(tree), font=10)
    myButton_Xoa_table.grid(row=1,column=4)
    myButton_exit = tk.Button(my_w_child, text="Exit", command=lambda: Exit(my_w_child), font=10)
    myButton_exit.grid(row=1, column=5)
#====================Kết thúc processing================================

#====================Bắt đầu registry ==================================
# Create Key
def InputDataCreateKey():
    crK = Toplevel(root)
    crK.geometry("500x200")
    crK.title("Create Key")

    path = Entry(crK, width=50, borderwidth=4, font=13)
    path.pack()
    path.insert(0, "Nhập đường dẫn cần tạo key vào đây...")

    new_key = Entry(crK, width=50, borderwidth=4, font=13)
    new_key.pack()
    new_key.insert(0, "Nhập key cần tạo vào đây...")

    btn_send = Button(crK, text="Send", command=lambda: createKey(path.get(), new_key.get()), borderwidth=3,
                      bg="orange", fg="blue", font=13)
    btn_send.pack()


def createKey(path, key):
    data = "Create key" + "$" + path + "$" + key
    s.sendall(bytes(data, "utf-8"))

    msg = s.recv(1024).decode("utf-8")
    if msg != "Lỗi":
        tkinter.messagebox.showinfo(title="Thông báo", message="Đã tạo key thành công")
    else:
        tkinter.messagebox.showinfo(title="Thông báo", message="Lỗi")
        InputDataCreateKey()


# Get value
def InputDataGetValue():
    getVal = Toplevel(root)
    getVal.geometry("500x200")
    getVal.title("Get value")

    path = Entry(getVal, width=50, borderwidth=4, font=13)
    path.pack()
    path.insert(0, "Nhập đường dẫn vào đây...")

    name_val = Entry(getVal, width=50, borderwidth=4, font=13)
    name_val.pack()
    name_val.insert(0, "Nhập tên của giá trị cần lấy...")

    btn_send = Button(getVal, text="Send", command=lambda: getValue(path.get(), name_val.get()), borderwidth=3,
                      bg="orange", fg="blue", font=13)
    btn_send.pack()


def getValue(path, nameVal):
    data = "Get value" + "$" + path + "$" + nameVal
    s.sendall(bytes(data, "utf-8"))

    msg = s.recv(1024).decode("utf-8")
    value = s.recv(1024).decode("utf-8")

    if value != "Lỗi":
        tkinter.messagebox.showinfo(title="Thông báo", message="Giá trị là: " + value)
    else:
        tkinter.messagebox.showinfo(title="Thông báo", message="Lỗi")
        InputDataGetValue()


# Set value
def InputDataSetValue():
    setVal = Toplevel(root)
    setVal.geometry("500x300")
    setVal.title("Set value")

    path = Entry(setVal, width=50, borderwidth=4, font=13)
    path.pack()
    path.insert(0, "Nhập đường cần tạo giá trị vào đây...")

    name_val = Entry(setVal, width=50, borderwidth=4, font=13)
    name_val.pack()
    name_val.insert(0, "Nhập tên của giá trị cần tạo...")

    val = Entry(setVal, width=50, borderwidth=4, font=13)
    val.pack()
    val.insert(0, "Nhập giá trị cần tạo...")

    clicked = StringVar(setVal)
    clicked.set("String")
    label = Label(setVal, text="Chọn dữ kiểu dữ liệu: ", font=13)
    label.place(x=1, y=100)
    typeVal = OptionMenu(setVal, clicked, "String", "Binary", "DWORD", "QWORD", "Multi-string", "Expand string")
    typeVal.pack()
    typeVal = clicked.get()

    btn_send = Button(setVal, text="Send", command=lambda: setValue(path.get(), name_val.get(), val.get(), typeVal),
                      borderwidth=3, bg="orange", fg="blue", font=13)
    btn_send.pack()


def setValue(path, nameVal, val, typeVal):
    data = "Set value" + "$" + path + "$" + nameVal + "$" + val + "$" + typeVal
    s.sendall(bytes(data, "utf-8"))

    msg = s.recv(1024).decode("utf-8")

    if msg != "Lỗi":
        tkinter.messagebox.showinfo(title="Thông báo", message=msg)
    else:
        tkinter.messagebox.showinfo(title="Thông báo", message="Lỗi")
        InputDataSetValue()


# Delete Key
def InputDataDeleteKey():
    delKey = Toplevel(root)
    delKey.geometry("500x200")
    delKey.title("Delete key")

    path = Entry(delKey, width=50, borderwidth=4, font=13)
    path.pack()
    path.insert(0, "Nhập đường dẫn cần xóa key vào đây...")

    btn_send = Button(delKey, text="Send", command=lambda: deleteKey(path.get()), borderwidth=3, bg="orange", fg="blue",
                      font=13)
    btn_send.pack()


def deleteKey(path):
    data = "Delete key" + "$" + path
    s.sendall(bytes(data, "utf-8"))

    msg = s.recv(1024).decode("utf-8")

    if msg != "Lỗi":
        tkinter.messagebox.showinfo(title="Thông báo", message=msg)
    else:
        tkinter.messagebox.showinfo(title="Thông báo", message="Lỗi")
        InputDataDeleteValue()


# Delete value
def InputDataDeleteValue():
    delVal = Toplevel(root)
    delVal.geometry("500x200")
    delVal.title("Delete value")

    path = Entry(delVal, width=50, borderwidth=4, font=13)
    path.pack()
    path.insert(0, "Nhập đường dẫn cần xóa value vào đây...")

    name_val = Entry(delVal, width=50, borderwidth=4, font=13)
    name_val.pack()
    name_val.insert(0, "Nhập tên của giá trị cần xóa...")

    btn_send = Button(delVal, text="Send", command=lambda: deleteValue(path.get(), name_val.get()), borderwidth=3,
                      bg="orange", fg="blue", font=13)
    btn_send.pack()


def deleteValue(path, nameVal):
    data = "Delete value" + "$" + path + "$" + nameVal
    s.sendall(bytes(data, "utf-8"))

    msg = s.recv(1024).decode("utf-8")

    if msg != "Lỗi":
        tkinter.messagebox.showinfo(title="Thông báo", message=msg)
    else:
        tkinter.messagebox.showinfo(title="Thông báo", message="Lỗi")
        InputDataDeleteValue()


# Quit
def Quit(handle):
    msg = "quit_registry"
    s.sendall(bytes(msg, "utf-8"))
    tkinter.messagebox.showinfo(title="Thông báo", message="Đã thoát chương trình")
    handle.destroy()


def Registry():
    msg = "registry"
    s.sendall(bytes(msg,"utf8"))
    handle = Toplevel(root)
    handle.geometry("255x270")
    handle.title("Handle Registry")

    btn_create_key = Button(handle, text="Create key", padx=30, pady=30, borderwidth=5, command=InputDataCreateKey)
    btn_create_key.grid(row=0, column=0)

    btn_get_value = Button(handle, text="Get value", padx=29.6, pady=30, borderwidth=5, command=InputDataGetValue)
    btn_get_value.grid(row=0, column=1)

    btn_set_value = Button(handle, text="Set value", padx=33, pady=30, borderwidth=5, command=InputDataSetValue)
    btn_set_value.grid(row=1, column=0)

    btn_del_value = Button(handle, text="Delete value", padx=22, pady=30, borderwidth=5, command=InputDataDeleteValue)
    btn_del_value.grid(row=1, column=1)

    btn_del_key = Button(handle, text="Delete key", padx=30, pady=30, borderwidth=5, command=InputDataDeleteKey)
    btn_del_key.grid(row=2, column=0)

    btn_quit = Button(handle, text="Exit", padx=44, pady=30, borderwidth=5, command=lambda : Quit(handle))
    btn_quit.grid(row=2, column=1)

#====================Kết thúc registry =================================


def Thoat():
    msg = "QUIT"
    s.sendall(bytes(msg, "utf8"))
    s.close()
    root.destroy()


# -------------main-----------------

root = tk.Tk()
root.geometry("400x300")
root.title("App")

entry = tk.Entry()
entry.grid(row=1, column=1)
myButton_connect = tk.Button(text="Connect", command=ConnectToServer)
myButton_connect.grid(row=1, column=2)
myButton_TakePic = tk.Button(text="Take screenshot", command=w_takeScreen, font=10)
myButton_TakePic.grid(row=2, column=1)
myButton_Process = tk.Button(text="Process Running", command=my_open, font=10)
myButton_Process.grid(row=3, column=1)
myButton_registry = tk.Button(text="Sửa Registry", command=Registry)
myButton_registry.grid(row=3, column=2)
myButton_Exit = tk.Button(text="Quit", command=Thoat, font=10)
myButton_Exit.grid(row=4, column=1)
root.mainloop()