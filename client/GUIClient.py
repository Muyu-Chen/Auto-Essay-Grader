import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ctypes import windll
import requests
import json
import pandas as pd
import numpy as np
from os import path, system
import openpyxl
import xlrd
from winsound import Beep
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import queue
from time import sleep
from pyautogui import position, moveTo
import subprocess
from language import *  # import language variables

Debug_mode = False
version = "2.3.1"

thisDir = path.dirname(path.abspath(__file__))
configCandidates = [
    path.join(thisDir, "..", "src", "config.json"),
    path.join(thisDir, "config.json"),
]
configFile = next((item for item in configCandidates if path.exists(item)), configCandidates[0])

print("version: ", version)
print("config.json is located at: ", configFile)
update_code = 0
try:
    # 调用可执行文件 目前需要修改的内容
    exe_path = path.join(thisDir, "support.exe")
    result = subprocess.Popen(
        # 需要修改
        [
            exe_path,
            "-version",
            version,
            "-url",
            "http://47.109.109.48/programs/essayJudgement/version.json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8-sig",
    )
    # 等待程序执行完成并获取输出
    stdout, stderr = result.communicate()
    print("return code:", result.returncode)
    print("标准输出:", stdout)
    print("错误输出:", stderr)
    if result.returncode == 1:
        print("返回值为1，需要更新")
        print("Exiting due to update requirement.")
        exit(0)
    else:
        print(f"返回值为{result.returncode}, 无需更新")
except Exception as e:
    print(f"更新过程中发生错误: {e}")

result_queue = queue.Queue()
isProcessRunning = False
stop_threads = False
try:
    with open(configFile, "r", encoding="utf-8-sig") as file:
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


serverAddress = config.get("frontend", {}).get("serverAddress", "http://127.0.0.1")
port = config.get("backend", {}).get("port", "5000")
serverUrl = "".join([serverAddress, ":", str(port), "/chat"])
serverUrlLogin = "".join([serverAddress, ":", str(port), "/login"])
serverUrlRegister = "".join([serverAddress, ":", str(port), "/register"])
serverUrlCharge = "".join([serverAddress, ":", str(port), "/charge"])
serverUrlData = "".join([serverAddress, ":", str(port), "/getData"])
# fileName
promptFileAddress = config.get("frontend", {}).get("promptFileAddress")
if not promptFileAddress:
    promptFileAddress = config.get("frontend", {}).get(
        "prompt_file_address", "criteria.txt"
    )
rulePlaySettingsAddress = config.get("frontend", {}).get(
    "rulePlaySettings", "rulePlaySettings.txt"
)
firstPromptAddress = config.get("frontend", {}).get("firstPrompt", "firstPrompt.txt")

promptFileAddress = (
    promptFileAddress
    if path.isabs(promptFileAddress)
    else path.join(thisDir, promptFileAddress)
)
rulePlaySettingsAddress = (
    rulePlaySettingsAddress
    if path.isabs(rulePlaySettingsAddress)
    else path.join(thisDir, rulePlaySettingsAddress)
)
promptFirstFileAddress = (
    firstPromptAddress
    if path.isabs(firstPromptAddress)
    else path.join(thisDir, firstPromptAddress)
)

width_default_value = config.get("frontend", {}).get("width_default_value", 30)
languageSetting = config.get("frontend", {}).get("language", "zh")
availableModels = config.get("frontend", {}).get("availableModels")
defaultUserAccount = config.get("frontend", {}).get(
    "userAccount", "please enter your Account"
)
defaultUserPassword = config.get("frontend", {}).get("userPassword", "")
balance_label = None

try:
    with open(promptFileAddress, "r", encoding="utf-8-sig") as file:
        criteriaInFile = file.read()
except FileNotFoundError:
    print(f"The file {promptFileAddress} was not found.")
    criteriaInFile = ""
except Exception as e:
    print(f"An unexpected error occurred while reading {promptFileAddress}: {e}")
    criteriaInFile = ""

try:
    with open(rulePlaySettingsAddress, "r", encoding="utf-8-sig") as file:
        rulePlaySettings = file.read()
except FileNotFoundError:
    print(f"The file {rulePlaySettingsAddress} was not found.")
    rulePlaySettings = ""
except Exception as e:
    print(f"An unexpected error occurred while reading {rulePlaySettingsAddress}: {e}")
    rulePlaySettings = ""

try:
    with open(promptFirstFileAddress, "r", encoding="utf-8-sig") as file:
        systemPromptFirst = file.read()
except FileNotFoundError:
    print(f"The file {promptFirstFileAddress} was not found.")
    systemPromptFirst = ""
except Exception as e:
    print(f"An unexpected error occurred while reading {promptFirstFileAddress}: {e}")
    systemPromptFirst = ""

ruleOutputFormat = """**输出格式**：
    - 使用JSON格式输出，包含以下两个键：
    - `comment`：对每个评分维度的简要评语，说明评分分值、扣分多少和理由。
    - `totalGrade`：计算所有维度分值和。
    必须包含、且仅包含键comment和totalGrade."""


def process_essay(model, file_path, columns, title, criteria, sheet_number):
    modelFirst = "qwen-plus"  # 对作文进行问题识别
    modelSecond = "qwen-plus"  # 检查问题识别的结果
    # modelThird # 对作文进行分项评分
    modelForth = "qwen-plus"
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

    systemContentFirst = systemPromptFirst
    systemContentSecond = systemContentFirst
    systemContentThird = f"""{rulePlaySettings}\n 需评分的作文写作要求:“ {title}”\n评分标准: {criteria}。"""

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

    with open(configFile, "r", encoding="utf-8-sig") as file:
        configNow = json.load(file)
        userAccount = configNow["frontend"]["userAccount"]
        userPassword = configNow["frontend"]["userPassword"]
    messages_list = ToArray(file_path, cols, sheet_number)
    url = serverUrl  # 指向 Flask 后端
    headers = {"Content-Type": "application/json"}
    responses = []  # 初始化一个空列表来存储响应

    input_directory = path.dirname(file_path)
    print(input_directory)
    output_file_path = path.join(input_directory, "output.csv")
    output_file_path_log = path.join(input_directory, "log.output.csv")
    # 清空文件内容，添加表头
    try:
        with open(output_file_path, "w", encoding="utf-8-sig") as f:
            f.write("Grade, Comment\n")

        with open(output_file_path_log, "w", encoding="utf-8-sig") as f:
            f.write("第一轮输出（指出作文存在的问题）,第二轮输出（在第一轮的基础上再次确认问题）,第三轮输出（前两轮的基础上输出评分）,\n")
    except Exception as e:
        output_file_path = path.join(input_directory, "output_2.csv")
        output_file_path_log = path.join(input_directory, "log.output_2.csv")
        try:
            with open(output_file_path, "w", encoding="utf-8-sig") as f:
                f.write("Grade, Comment\n")
            with open(output_file_path_log, "w", encoding="utf-8-sig") as f:
                f.write("第一轮输出（指出作文存在的问题）,第二轮输出（在第一轮的基础上再次确认问题）,第三轮输出（前两轮的基础上输出评分）,\n")
        except Exception as e:
            return "Error: " + str(e)
    for message in messages_list:

        def keepAlive():
            current_position = position()  # 获取当前鼠标位置
            new_position = (current_position[0] + 1, current_position[1])  # 右移1像素
            moveTo(new_position)  # 移动鼠标
            moveTo(current_position)  # 移回原位置

        keepAlive()
        print(
            "\n—————————————————————————————passage begin—————————————————————————————"
        )
        # 打印前30个字符的消息内容
        firstTimeMessage = (
            f"""请根据以下评分标准，对题目为“{title}”的内容进行点评：\n{message}"""
        )
        print("Passage: ", (message[:60]).replace("\n", " "))
        firstTime = {
            "messages": firstTimeMessage,
            "model": modelFirst,
            "systemContent": systemContentFirst,
            "userAccount": userAccount,
            "userPassword": userPassword,
            "jsonOrNot": "false",
        }
        responseFirst = requests.post(url, headers=headers, data=json.dumps(firstTime))
        responseFirst_content = responseFirst.content.decode("utf-8")
        if not (responseFirst.status_code == 200):
            return "Error: " + responseFirst_content
        try:
            with open(output_file_path_log, "a", encoding="utf-8-sig") as f:
                f.write(
                    response_content.replace(",", "，")
                    .replace("\n", " ")
                    .replace("\r", " ")
                    + ",\n"
                )
        except Exception as e:
            print("Error: 第一轮日志输出错误： " + str(e))
        print("before 2nd")
        secondTimeMessage = f"""{firstTimeMessage} **assistant:** \n第一部分文章评分结果: \n{responseFirst_content}. 请再次全面识别问题，检查其中是否有不符合原文的虚假错误信息，如果有，请删除该错误信息；若有遗漏，请补充完整。并按照上文提及的输出要求，再次输出点评。"""
        secondTime = {
            "messages": secondTimeMessage,
            "model": modelSecond,
            "systemContent": systemContentSecond,
            "userAccount": userAccount,
            "userPassword": userPassword,
            "jsonOrNot": "false",
        }
        response = requests.post(url, headers=headers, data=json.dumps(secondTime))
        response_content = response.content.decode("utf-8")
        try:
            with open(output_file_path_log, "a", encoding="utf-8-sig") as f:
                f.write(
                    response_content.replace(",", "，")
                    .replace("\n", " ")
                    .replace("\r", " ")
                    + ",\n"
                )
        except Exception as e:
            print("Error: 第二轮日志输出错误： " + str(e))
        print("——————————\n第二部分：\n" + response_content)
        keepAlive()

        print("before 3rd———————————————————————————")
        thirdTime = {
            "messages": f"""assistant: 文章内容：{message}.\n
            user: 请根据以下点评，对文章进行分项评分。评分需基于以下评分标准的多个维度与第一部分的文章评分结果已指出的问题，逐项说明扣分理由后，逐项评分。并结合标准评分维度和附加扣分项合理调整每项分数。**无需计算总分！** 
            - `comment`：包含每个评分维度的评分与简要评语，但不用提出修改意见。对于“额外扣分”部分，即使已经有具体扣分分值，也只扣问题严重的部分，不扣问题轻微的部分，不扣问题轻微的部分。对于文章整体较好的情况，不对中等的额外问题进行扣分。
            - `summary`: 一句话总结全文，不超过30字。\n\n
            第一部分文章评分结果，对于额外扣分项，请忽略轻微问题，只扣问题严重的部分；已在标准评分维度中考虑的问题不再在额外扣分处重复扣分。: 
              {response_content}""",
            "model": model,
            "systemContent": systemContentThird,
            "userAccount": userAccount,
            "userPassword": userPassword,
            "jsonOrNot": "false",
        }
        response = requests.post(url, headers=headers, data=json.dumps(thirdTime))
        response_content = response.content.decode("utf-8")
        print(response_content)
        if not (response.status_code == 200):
            return "Error: " + response_content
        try:
            with open(output_file_path_log, "a", encoding="utf-8-sig") as f:
                f.write(
                    response_content.replace(",", "，")
                    .replace("\n", " ")
                    .replace("\r", " ")
                    + ",\n"
                )
        except Exception as e:
            print("Error: 第三轮日志输出错误： " + str(e))

        print("before 4rd")
        systemContentForth = f"""你的任务是根据提供的评分结果，计算文章的总分，并以 JSON 格式输出结果。
                                **计算要求**：
                                - 每个评分维度的分数相加，（请注意，不计算!不计算!评分维度内写的扣分），并减去在**结尾**的附加扣分项，计算总分。
                                **输出要求**：
                                - JSON 格式包含以下两个键：
                                - `comment`：小于30字总结全文 + （不限字数）直接提取五个评分维度的评语，以及将五个评分维度的分数相加，并减去额外扣分项的计算过程。
                                - `totalGrade`：计算后的总分。"""
        forthTime = {
            "messages": f"""请根据以下评分的“分项评分总结”，对文章的评分进行计算（请注意，不计算评分维度内单独写的扣分）。结合文章中的分数计算总分。用JSON格式输出，包含以下两个键：
                - comment：总结全文的一句话 && 并包含所有评分维度的评语，不要缩句。输出你的分数计算过程。
                - `totalGrade`：分数之和\n\n
                文章评分结果: 
                {response_content}\n
                输出格式:
                {ruleOutputFormat}""",
            "model": modelForth,
            "systemContent": systemContentForth,
            "userAccount": userAccount,
            "userPassword": userPassword,
            "jsonOrNot": "true",
        }
        response = requests.post(url, headers=headers, data=json.dumps(forthTime))
        response_content = response.content.decode("utf-8")
        print("the final response content: ——————————————————————————————-")
        print(response_content)
        if not (response.status_code == 200):
            return "Error: " + response_content

        response_content = (
            response_content.replace("```json", "").replace("```", "").strip()
        )
        # print(response_content) # 打印响应内容 现在放后面了
        response_data = json.loads(response_content)

        grade = response_data.get("totalGrade")
        comment = response_data.get("comment")
        grade = (
            str(grade)
            .replace("\n", " ")
            .replace("\r", " ")
            .replace(",", "，")
            .replace("'", "")
        )
        comment = (
            str(comment)
            .replace("\n", "")
            .replace("\r", "")
            .replace(",", "，")
            .replace("{", "")
            .replace("}", "")
            .replace("'", "")
        )
        # 将评分和评论添加到列表中
        responseNew = f"{grade}, {comment}"
        responses.append(responseNew)

        print("————————————————————— the processed response —————————————————————")
        # print(response_content)
        # 打印响应内容 这个因为不具有调试价值，所以只打印前50个字符
        print(
            "(验证是否正确提取成绩) Response content: \n"
            + (grade + ", " + comment)[:50]
        )
        try:
            with open(output_file_path, "a", encoding="utf-8-sig") as f:
                f.write(responseNew + "\n")
        # 如果写入失败，等待8秒后再次尝试，共尝试3次
        except Exception as e:
            sleep(8)
            try:
                with open(output_file_path, "a", encoding="utf-8-sig") as f:
                    f.write(responseNew + "\n")
            except Exception as e:
                sleep(8)
                try:
                    with open(output_file_path, "a", encoding="utf-8-sig") as f:
                        f.write(responseNew + "\n")
                except Exception as e:
                    return "Error: " + str(e)
        print("—————————————————————————————passage end—————————————————————————————\n")

    frequency = 440  # 频率，单位为赫兹
    duration = 1200  # 持续时间 单位为毫秒
    Beep(frequency, duration)
    return output_file_path


# 获取Windows系统的DPI缩放比例
def get_dpi_scaling(window):
    user32 = windll.user32
    user32.SetProcessDPIAware()  # 让Python应用程序对高DPI显示器感知
    dpi = user32.GetDpiForWindow(window.winfo_id())  # 获取DPI值
    print("DPI:", dpi)
    scaling_factor = dpi / 96  # 96是标准DPI
    return scaling_factor


# 自动保存函数
def auto_save():
    update_balance()
    scoring_criteria = text_scoring_criteria.get("1.0", "end-1c")
    with open(promptFileAddress, "w", encoding="utf-8-sig") as file_write:
        file_write.write(scoring_criteria)
    # 每隔30s（30000毫秒）调用一次auto_save函数
    if isProcessRunning:
        program_main_window.after(120000, auto_save)
    else:
        program_main_window.after(30000, auto_save)


def program_main_window_func():
    global program_main_window
    # 创建主窗口
    # window = tk.Tk()
    program_main_window = TkinterDnD.Tk()  # 这个才支持拖入

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

    # 创建一个标签用于显示当前余额
    global balance_label
    balance_label = tk.Label(
        program_main_window,  # 父窗口
        text="Current Balance: ￥0.000",  # 标签初始文本
        anchor="e",  # 文本对齐方式为右对齐
        font=("Microsoft Yahei", 10),  # 字体设置为Arial，大小为12
        # bg="white",  # 背景颜色为白色
    )
    # 将标签放置在窗口的相对位置 (relx=0.9, rely=0.01)，锚点为右上角
    balance_label.place(relx=0.98, rely=0.01, anchor="ne")
    update_balance()
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
        file_path = path.normpath(file_path)  # 标准化文件路径
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
    entry_column_count.insert(
        "1.0",
        "B",
    )

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

    def process_in_thread():
        global isProcessRunning
        # 获取用户输入内容
        model_selected = model_var.get()
        file_name = entry_file_name.get("1.0", "end-1c")
        print(file_name)
        sheet_count = entry_sheet_count.get("1.0", "end-1c")
        column_count = entry_column_count.get("1.0", "end-1c")
        essay_title = text_essay_title.get("1.0", "end-1c")  # 获取大文本框内容
        scoring_criteria = text_scoring_criteria.get("1.0", "end-1c")
        print("现在在另外一个线程中处理中")
        with open(promptFileAddress, "w", encoding="utf-8-sig") as file_write:
            file_write.write(scoring_criteria)
        try:

            # 假设你要调用模型处理作文题目
            # result="result"
            # for i in range(10):
            #    sleep(0.5)
            #    print(f"模拟处理中... {i+1}/10")

            result = process_essay(
                model_selected,
                file_name,
                column_count,
                essay_title,
                scoring_criteria,
                sheet_count,
            )
            print("线程处理结束")
            result_queue.put({"status": "success", "result": result})
            # 其余在主线程中完成print("显示文件保存位置/错误信息: " + result)

        except Exception as e:
            result_queue.put({"status": "error", "error": str(e)})
            # messagebox.showerror("{TresultError}", f"{TresultErrorReason}{str(e)}")

    def clear_queue(q):
        """清空队列的所有内容"""
        try:
            while not q.empty():
                q.get_nowait()  # 非阻塞方式获取并移除队列中的所有内容
        except queue.Empty:
            pass

    # 主程序的处理逻辑
    def submit():
        global isProcessRunning
        # 禁用提交按钮，避免重复提交
        submit_button.config(state=tk.DISABLED)

        # 清空队列，确保没有遗留的结果

        isProcessRunning = True
        print("开始处理")
        num2 = 350 * scaling_factor
        geometry_str = f"{int(num2)}x{int(num2*0.65)}"  # 宽*高
        processing_window = tk.Toplevel(root)
        processing_window.title("处理中")
        tk.Label(
            processing_window,
            text="正在处理，请稍候... \n\n处理完成后该窗口会自动关闭，并有嗡鸣声作为提示。\n\n处理时间可能较长，请耐心等待。\n\n输出文件中“log.output.csv”为日志文件，第三次输出为作文的评分结果，可以做为批阅时的参考。",
            wraplength=250 * scaling_factor,
        ).pack(padx=20, pady=20)
        processing_window.geometry(geometry_str)

        # 禁用关闭按钮
        processing_window.protocol("WM_DELETE_WINDOW", lambda: None)

        def check_thread_result():
            """检查线程的结果"""
            global isProcessRunning
            try:
                result = result_queue.get_nowait()
                processing_window.destroy()
                submit_button.config(state=tk.NORMAL)
                if result["status"] == "error":
                    # 显示错误信息
                    messagebox.showerror("错误", f"处理失败: {result['error']}")
                elif result["status"] == "success":
                    # 显示成功信息
                    messagebox.showinfo("成功", f"文件保存在: {result['result']}")
                isProcessRunning = False
            except queue.Empty:
                # 队列为空，继续等待
                if isProcessRunning:
                    root.after(150, check_thread_result)
            except Exception as e:
                messagebox.showerror("错误", f"处理失败: {str(e)}")
                processing_window.destroy()
                submit_button.config(state=tk.NORMAL)
                isProcessRunning = False

        # 定期检查线程的结果

        def start_thread():
            thread = threading.Thread(target=process_in_thread)
            clear_queue(result_queue)
            thread.start()
            root.after(150, check_thread_result)

        # 开始检查线程结果
        root.after(2000, start_thread)

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


def update_balance():
    """
    更新右上角的余额显示
    """
    global balance_label
    with open(configFile, "r", encoding="utf-8-sig") as file:
        configNow = json.load(file)
        userAccount = configNow["frontend"]["userAccount"]
        userPassword = configNow["frontend"]["userPassword"]
    params = {
        "todo": "getBalance",
        "userAccount": userAccount,
        "userPassword": userPassword,
    }
    response = requests.get(serverUrlData, params=params)
    print(response)
    print(response.json())
    new_balance = response.json().get("currentBalance")
    balance_label.config(text=f"Current Balance: ￥{new_balance:.3f}")


def on_closing():
    global stop_threads
    if messagebox.askokcancel("退出", "你确定要退出吗?"):
        try:
            if login_window is not None and login_window.winfo_exists():
                stop_threads = True
                sleep(0.4)
                login_window.destroy()
        except NameError:
            pass

        try:
            if program_main_window is not None and program_main_window.winfo_exists():
                stop_threads = True
                sleep(0.4)
                program_main_window.destroy()
        except NameError:
            pass

        try:
            if root is not None and root.winfo_exists():
                stop_threads = True
                sleep(0.4)
                root.destroy()
        except NameError:
            pass


def checkIsAuthurized(userAccount, userPassword, version, isLogin=False):
    # 只有登录的时候才更新版本号
    # 在这里添加登录逻辑，例如检查用户名和密码是否正确
    url = serverUrlLogin  # 指向 Flask 后端
    headers = {"Content-Type": "application/json"}
    data = {
        "todo": "isVerified",
        "userAccount": userAccount,
        "userPassword": userPassword,
        "version": version,
        "isLogin": str(isLogin),  # 将 isLogin 转换为字符串
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response)
    print(response.json())
    if response.status_code == 200:
        return True


def userRegister(userAccount, userPassword, referredbyUID):
    url = serverUrlRegister  # 指向 Flask 后端
    headers = {"Content-Type": "application/json"}
    data = {
        "userAccount": userAccount,
        "userPassword": userPassword,
        "referredByUID": referredbyUID,
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response)
    print(response.json())
    if response.status_code == 201:
        # Update config.json with new user info
        with open(configFile, "r+", encoding="utf-8-sig") as file:
            config = json.load(file)
            config["frontend"]["userAccount"] = userAccount
            config["frontend"]["userPassword"] = userPassword
            config["frontend"]["UID"] = response.json().get("UID")
            # 使用 file.seek(0) 将文件指针移动到开头，再写入更新后的内容
            file.seek(0)
            json.dump(config, file, ensure_ascii=False, indent=4)
            # 使用 file.truncate() 清空文件剩余内容
            file.truncate()
        return True
    elif response.status_code == 400 or response.status_code == 500:
        return False


def login():
    def check_login():
        username = entry_username.get()
        password = entry_password.get()

        if checkIsAuthurized(username, password, version, True):  # 用户名和密码验证
            # Update config.json with new user info
            if defaultUserAccount != username or defaultUserPassword != password:
                with open(configFile, "r+", encoding="utf-8-sig") as file:
                    config = json.load(file)
                    config["frontend"]["userAccount"] = username
                    config["frontend"]["userPassword"] = password
                    config["frontend"]["UID"] = "new user"
                    # 使用 file.seek(0) 将文件指针移动到开头，再写入更新后的内容
                    file.seek(0)
                    json.dump(config, file, ensure_ascii=False, indent=4)
                    # 使用 file.truncate() 清空文件剩余内容
                    file.truncate()
            login_window.destroy()
            program_main_window_func()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")

    def open_register_window():

        register_window = tk.Toplevel(root)
        register_window.title("注册")
        factor = get_dpi_scaling(register_window)
        num1 = 340 * factor
        geometry_str = f"{int(num1)}x{int(num1)}"  # 宽*高
        register_window.geometry(geometry_str)

        tk.Label(register_window, text="用户名:").pack(pady=5)
        entry_new_username = tk.Entry(register_window)
        entry_new_username.pack(pady=5)

        tk.Label(register_window, text="推荐码:").pack(pady=5)
        entry_refer_UID = tk.Entry(register_window)
        entry_refer_UID.pack(pady=5)

        tk.Label(register_window, text="密码:").pack(pady=5)
        entry_new_password = tk.Entry(register_window, show="*")
        entry_new_password.pack(pady=5)

        tk.Label(register_window, text="确认密码:").pack(pady=5)
        entry_confirm_password = tk.Entry(register_window, show="*")
        entry_confirm_password.pack(pady=5)

        def register():
            newUserAccount = entry_new_username.get()
            referredbyUID = entry_refer_UID.get()
            newUserPassword = entry_new_password.get()
            confirm_password = entry_confirm_password.get()

            if newUserPassword == confirm_password:
                if userRegister(newUserAccount, newUserPassword, str(referredbyUID)):
                    messagebox.showinfo("注册成功", "注册成功，请返回登录")
                    register_window.destroy()
                else:
                    messagebox.showerror("注册失败", "用户已存在")
            else:
                messagebox.showerror("注册失败", "密码不匹配")

        tk.Button(register_window, text="注册", command=register).pack(pady=20)

    global login_window
    global root
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    login_window = tk.Toplevel(root)  # 创建独立的登录窗口
    login_window.protocol("WM_DELETE_WINDOW", on_closing)

    # 设置窗口大小
    scaling_factor = get_dpi_scaling(login_window)
    # num1 = 200 * scaling_factor
    num1 = 250 * scaling_factor
    geometry_str = f"{int(num1)}x{int(num1*0.8)}"  # 宽*高

    login_window.geometry(geometry_str)
    # 修复成功，通过导入pyautogui库，这个问题就消失了
    # 这里有bug 如果这里设置了缩放
    # 设置缩放过后，后面的那个窗口会变得很小，所以这里不设置缩放
    # 我排查过后应该是库的问题
    ## window.tk.call("tk", "scaling", 2)  # 将缩放比例设置为2倍
    ## 自动检测DPI并进行适配
    ## scaling_factor = get_dpi_scaling()
    # login_window.tk.call("tk", "scaling", scaling_factor * 1.5)

    login_window.title(Tlogin)

    tk.Label(login_window, text=TuserName).pack(pady=5)
    entry_username = tk.Entry(login_window)
    entry_username.pack(pady=5)
    entry_username.insert(0, defaultUserAccount)

    tk.Label(login_window, text=Tlogin).pack(pady=5)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack(pady=5)
    entry_password.insert(0, defaultUserPassword)

    tk.Button(login_window, text=Tlogin, command=check_login).pack(pady=10)
    register_label = tk.Label(login_window, text=TsignUp, fg="blue", cursor="hand2")
    register_label.pack(pady=10)
    register_label.bind("<Button-1>", lambda e: open_register_window())

    login_window.mainloop()


login()
# main_window()
