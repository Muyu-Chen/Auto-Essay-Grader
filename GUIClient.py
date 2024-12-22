import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ctypes
import requests
import json
import pandas as pd
import numpy as np
import os
import openpyxl
import xlrd
import winsound
from tkinterdnd2 import DND_FILES, TkinterDnD
from language import *  # import language variables

try:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
except FileNotFoundError:
    print("The config.json file was not found.")
    config = {}
except json.JSONDecodeError:
    print("Error decoding JSON from the config.json file.")
    config = {}
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    config = {}


serverAddress = config.get("frontend", {}).get("serverAddress", "http://localhost")
port = config.get("backend", {}).get("port", "5000")
serverUrl = "".join([serverAddress, ":", str(port), "/chat"])
promptFileAddress = config.get("frontend", {}).get(
    "prompt_file_address", "criteria.txt"
)
rulePlaySettingsAddress = config.get("frontend", {}).get(
    "rulePlaySettings", "rulePlaySettings.txt"
)
width_default_value = config.get("frontend", {}).get("width_default_value", 30)
languageSetting = config.get("frontend", {}).get("language", "zh")
availableModels = config.get("frontend", {}).get("availableModels")


try:
    with open(promptFileAddress, "r", encoding="utf-8") as file:
        criteriaInFile = file.read()
except FileNotFoundError:
    print(f"The file {promptFileAddress} was not found.")
    criteriaInFile = ""
except Exception as e:
    print(f"An unexpected error occurred while reading {promptFileAddress}: {e}")
    criteriaInFile = ""

try:
    with open(rulePlaySettingsAddress, "r", encoding="utf-8") as file:
        rulePlaySettings = file.read()
except FileNotFoundError:
    print(f"The file {rulePlaySettingsAddress} was not found.")
    rulePlaySettings = ""
except Exception as e:
    print(f"An unexpected error occurred while reading {rulePlaySettingsAddress}: {e}")
    rulePlaySettings = ""

rulePlaySettings = (
    rulePlaySettings
    + "要求以JSON格式输出，其中包含、且仅包含以下键：totalGrade、comment。不要包含任何其他内容。"
)


def process_essay(model, file_path, columns, title, criteria, sheet_number):
    if columns == "A" or columns == "1" or columns == "a":
        cols = [0]  # 假设你要读取第1列（A列）
        pass
    elif columns == "B" or columns == "2" or columns == "b":
        cols = [1]  # 假设你要读取第2列（B列）
        pass
    elif columns == "C" or columns == "3" or columns == "c":
        cols = [2]
        pass
    elif columns == "D" or columns == "4" or columns == "d":
        cols = [3]
        pass
    elif columns == "E" or columns == "5" or columns == "e":
        cols = [4]
        pass
    elif columns == "F" or columns == "6" or columns == "f":
        cols = [5]
        pass
    elif columns == "G" or columns == "7" or columns == "g":
        cols = [6]
        pass
    elif columns == "H" or columns == "8" or columns == "h":
        cols = [7]
        pass
    elif columns == "I" or columns == "9" or columns == "i":
        cols = [8]
        pass
    elif columns == "J" or columns == "10" or columns == "j":
        cols = [9]
        pass
    elif columns == "K" or columns == "11" or columns == "k":
        cols = [10]
        pass
    elif columns == "L" or columns == "12" or columns == "l":
        cols = [11]
        pass
    elif columns == "M" or columns == "13" or columns == "m":
        cols = [12]
        pass
    elif columns == "N" or columns == "14" or columns == "n":
        cols = [13]
        pass
    elif columns == "O" or columns == "15" or columns == "o":
        cols = [14]
        pass
    sheet_number = int(sheet_number) - 1
    systemContent = f"""{rulePlaySettings} 题目:“ {title}”\n评分标准: {criteria}"""

    df = pd.read_excel(file_path)

    def ToArray(file_path, cols, sheet_number):
        # 读取 Excel 文件，指定列和工作表名称
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        FunctionRead = pd.read_excel(
            file_path, usecols=cols, sheet_name=sheet_names[sheet_number], header=None
        )
        # 将数据转换为 NumPy 数组
        FunctionArray = np.array(FunctionRead.stack())
        return FunctionArray

    messages_list = ToArray(file_path, cols, sheet_number)
    url = serverUrl  # 指向 Flask 后端
    headers = {"Content-Type": "application/json"}
    responses = []  # 初始化一个空列表来存储响应
    for message in messages_list:
        print("Message:", message)
        data = {"messages": message, "model": model, "systemContent": systemContent}
        response = requests.post(url, headers=headers, data=json.dumps(data))

        print(response)
        response_content = response.content.decode("utf-8")
        print(response_content)
        response_content = (
            response_content.replace("```json", "").replace("```", "").strip()
        )
        print(response_content)
        response_data = json.loads(response_content)

        grade = response_data.get("totalGrade")
        comment = response_data.get("comment")
        grade = str(grade).replace("\n", "").replace("\r", "").replace(",", "，")
        comment = str(comment).replace("\n", "").replace("\r", "").replace(",", "，")
        # 将评分和评论添加到列表中
        responses.append(grade + ", " + comment)
        # 打印响应内容 这个因为不具有调试价值，所以只打印前50个字符
        print("Response content: " + (grade + ", " + comment)[:50])

    input_directory = os.path.dirname(file_path)
    output_file_path = os.path.join(input_directory, "output.csv")

    with open(output_file_path, "w", encoding="ANSI") as f:
        for response in responses:
            f.write(response + "\n")
    frequency = 440  # 频率，单位为赫兹
    duration = 1200  # 持续时间 单位为毫秒
    winsound.Beep(frequency, duration)
    return output_file_path


# 获取Windows系统的DPI缩放比例
def get_dpi_scaling(window):
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()  # 让Python应用程序对高DPI显示器感知
    dpi = user32.GetDpiForWindow(window.winfo_id())  # 获取DPI值
    print("DPI:", dpi)
    scaling_factor = dpi / 96  # 96是标准DPI
    return scaling_factor


def auto_save():
    scoring_criteria = text_scoring_criteria.get("1.0", "end-1c")
    with open("criteria.txt", "w", encoding="utf-8") as file_write:
        file_write.write(scoring_criteria)
    # 每隔30s（30000毫秒）调用一次auto_save函数
    program_main_window.after(30000, auto_save)


def program_main_window_func():
    global program_main_window
    # 创建主窗口
    # window = tk.Tk()
    program_main_window = TkinterDnD.Tk()  # 这个才支持拖入

    # 自动保存函数

    program_main_window.title("英语作文评分工具")

    # 设置窗口大小
    scaling_factor = get_dpi_scaling(program_main_window)
    num1 = 600 * scaling_factor
    geometry_str = f"{int(num1)}x{int(num1*1.3)}"  # 宽*高
    program_main_window.geometry(geometry_str)
    # window.tk.call("tk", "scaling", 2)  # 将缩放比例设置为2倍
    # 自动检测DPI并进行适配
    # scaling_factor = get_dpi_scaling()
    program_main_window.tk.call("tk", "scaling", scaling_factor * 1.5)

    # 设置窗口关闭时的处理逻辑
    program_main_window.protocol("WM_DELETE_WINDOW", on_closing)

    # 说明文本（将要集合在language.py中）
    instructions = Tinstructions
    label_instructions = tk.Label(
        program_main_window,
        text=instructions,
        justify="left",
        wraplength=500 * scaling_factor,
    )
    label_instructions.pack(pady=10)

    # 模型选择下拉栏
    label_model = tk.Label(program_main_window, text=TchoosingModel)
    label_model.pack()

    model_var = tk.StringVar()
    model_dropdown = ttk.Combobox(
        program_main_window, textvariable=model_var, state="readonly"
    )
    model_dropdown["values"] = availableModels
    model_dropdown.pack(pady=5)

    # 文件名称输入框
    label_file_name = tk.Label(program_main_window, text=TfilePath)
    label_file_name.pack()

    # 使用 tk.Text 并设置高度为 height 行
    entry_file_name = tk.Text(
        program_main_window, height=2.3, width=int(width_default_value * scaling_factor)
    )
    entry_file_name.pack(pady=5)

    # 定义拖放事件处理函数
    def drop(event):
        file_path = event.data.strip("{}")
        file_path = os.path.normpath(file_path)  # 标准化文件路径
        entry_file_name.delete(1.0, tk.END)  # 清空现有内容
        entry_file_name.insert(1.0, file_path)  # 将拖放的文件路径插入输入框

    # 注册拖放功能
    entry_file_name.drop_target_register(DND_FILES)  # 注册为文件拖放目标
    entry_file_name.dnd_bind("<<Drop>>", drop)  # 绑定拖放事件

    # 输入工作表数输入框
    label_sheet_count = tk.Label(program_main_window, text=TsheetNumber)
    label_sheet_count.pack()

    entry_sheet_count = tk.Text(
        program_main_window, height=2, width=int(width_default_value * scaling_factor)
    )
    entry_sheet_count.pack(pady=5)
    entry_sheet_count.insert("1.0", "1")

    # 输入列数输入框
    label_column_count = tk.Label(program_main_window, text=TcolumnNumber)
    label_column_count.pack()

    entry_column_count = tk.Text(
        program_main_window, height=2, width=int(width_default_value * scaling_factor)
    )
    entry_column_count.pack(pady=5)

    # 作文题目输入框（大文本框）
    label_essay_title = tk.Label(program_main_window, text=TessayTitle)
    label_essay_title.pack()

    text_essay_title = tk.Text(
        program_main_window, height=4.5, width=int(width_default_value * scaling_factor)
    )
    text_essay_title.pack(pady=5)
    text_essay_title.insert(
        "1.0",
        TessayTitleExample,
    )

    # 评分标准输入框（大文本框）
    label_scoring_criteria = tk.Label(program_main_window, text=Tscoring_criteria)
    label_scoring_criteria.pack()
    global text_scoring_criteria
    text_scoring_criteria = tk.Text(
        program_main_window, height=9.5, width=int(width_default_value * scaling_factor)
    )
    text_scoring_criteria.pack(pady=5)
    text_scoring_criteria.insert(
        "1.0",
        criteriaInFile,
    )  # 设置默认值

    # 提交按钮
    submit_button = tk.Button(
        program_main_window, text=Tsubmit, state=tk.DISABLED
    )  # 默认禁用

    # 主程序的处理逻辑
    def submit():
        # 禁用提交按钮，避免重复提交
        submit_button.config(state=tk.DISABLED)

        # 获取用户输入内容
        model_selected = model_var.get()
        file_name = entry_file_name.get("1.0", "end-1c")
        sheet_count = entry_sheet_count.get("1.0", "end-1c")
        column_count = entry_column_count.get("1.0", "end-1c")
        essay_title = text_essay_title.get("1.0", "end-1c")  # 获取大文本框内容
        scoring_criteria = text_scoring_criteria.get("1.0", "end-1c")
        with open("criteria.txt", "w", encoding="utf-8") as file_write:
            file_write.write(scoring_criteria)

        try:
            # 假设你要调用模型处理作文题目
            result = process_essay(
                model_selected,
                file_name,
                column_count,
                essay_title,
                scoring_criteria,
                sheet_count,
            )

            # 显示处理结果
            messagebox.showinfo("{Tresult}", f"{TresultContent}{result}")

        except Exception as e:
            messagebox.showerror("{TresultError}", f"{TresultErrorReason}{str(e)}")

        finally:
            # 当处理完成后重新启用提交按钮（如果有内容变化的话）
            submit_button.config(state=tk.NORMAL)

    # 当用户修改任何输入时启用按钮
    def enable_submit(*args):
        submit_button.config(state=tk.NORMAL)

    # 绑定输入框的修改事件到 enable_submit
    model_var.trace_add("write", enable_submit)
    entry_file_name.bind("<KeyRelease>", lambda event: enable_submit())
    entry_column_count.bind("<KeyRelease>", lambda event: enable_submit())
    text_essay_title.bind("<KeyRelease>", lambda event: enable_submit())
    text_scoring_criteria.bind("<KeyRelease>", lambda event: enable_submit())

    # 提交按钮
    submit_button.config(command=submit)
    submit_button.pack(pady=20)

    # 自动保存函数
    program_main_window.after(30000, auto_save)
    # 进入主循环
    program_main_window.mainloop()


def on_closing():
    if messagebox.askokcancel("退出", "你确定要退出吗?"):
        try:
            if login_window is not None and login_window.winfo_exists():
                login_window.destroy()
        except NameError:
            pass

        try:
            if program_main_window is not None and program_main_window.winfo_exists():
                program_main_window.destroy()
        except NameError:
            pass

        try:
            if root is not None and root.winfo_exists():
                root.destroy()
        except NameError:
            pass


def login():
    def check_login():
        username = entry_username.get()
        password = entry_password.get()
        if str(username) == "1" and str(password) == "1":  # 简单的用户名和密码验证
            login_window.destroy()
            program_main_window_func()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")
    global login_window
    global root
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    login_window = tk.Toplevel(root)  # 创建独立的登录窗口
    login_window.protocol("WM_DELETE_WINDOW", on_closing)

    # 设置窗口大小
    #scaling_factor = get_dpi_scaling(login_window)
    #num1 = 200 * scaling_factor
    num1=270
    geometry_str = f"{int(num1)}x{int(num1*0.8)}"  # 宽*高
    login_window.geometry(geometry_str)
    ## window.tk.call("tk", "scaling", 2)  # 将缩放比例设置为2倍
    ## 自动检测DPI并进行适配
    ## scaling_factor = get_dpi_scaling()
    #login_window.tk.call("tk", "scaling", scaling_factor * 1.5)

    login_window.title("登录")

    tk.Label(login_window, text="用户名:").pack(pady=5)
    entry_username = tk.Entry(login_window)
    entry_username.pack(pady=5)

    tk.Label(login_window, text="密码:").pack(pady=5)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack(pady=5)

    tk.Button(login_window, text="登录", command=check_login).pack(pady=20)

    login_window.mainloop()


login()
# main_window()
