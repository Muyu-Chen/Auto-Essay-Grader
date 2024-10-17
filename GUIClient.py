import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ctypes
import requests
import json
import pandas as pd
import numpy as np
import os
import winsound
from tkinterdnd2 import DND_FILES, TkinterDnD

# please replace the following with your server address
serverUrl="http://localhost:5000/chat" # follow the format of "http://ip:port/chat"


# 获取Windows系统的DPI缩放比例
def get_dpi_scaling():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()  # 让Python应用程序对高DPI显示器感知
    dpi = user32.GetDpiForWindow(window.winfo_id())  # 获取DPI值
    print("DPI:", dpi)
    scaling_factor = dpi / 96  # 96是标准DPI
    return scaling_factor


# 创建主窗口
# window = tk.Tk()
window = TkinterDnD.Tk()  # 这个才支持拖入

window.title("英语作文评分工具")

# 设置窗口大小
scaling_factor = get_dpi_scaling()
num1 = 600 * scaling_factor
geometry_str = f"{int(num1)}x{int(num1*1.24)}"
window.geometry(geometry_str)
# window.tk.call("tk", "scaling", 2)  # 将缩放比例设置为2倍
# 自动检测DPI并进行适配
# scaling_factor = get_dpi_scaling()
window.tk.call("tk", "scaling", scaling_factor * 1.5)

# 说明文本
instructions = """                                欢迎使用作文评分工具！
1. 选择你要使用的模型：max性能好价格高，
   plus最推荐，turbo性能差价格低
2. 将表格中的表头删除，只保留作文内容，
   然后保存为xls文件（不建议xlsx，但是可以运行）。
2. 拖入文件到文件路径，并输入作文对应的列数。
3. 填写作文题目及评分标准，然后点击提交（随后等待即可）。
4. 开源地址：https://github.com/Muyu-Chen/Auto-Essay-Grader"""
label_instructions = tk.Label(
    window, text=instructions, justify="left", wraplength=500 * scaling_factor
)
label_instructions.pack(pady=10)

# 模型选择下拉栏
label_model = tk.Label(window, text="选择模型/choose a model（默认为turbo):")
label_model.pack()

model_var = tk.StringVar()
model_dropdown = ttk.Combobox(window, textvariable=model_var, state="readonly")
model_dropdown["values"] = (
    "qwen-max",
    "qwen-max-0919",
    "qwen-plus",
    "qwen-plus-latest",
    "qwen-plus-0919",
    "qwen-plus-0806",
    "qwen-turbo",
    "qwen-turbo-0919",
)  # 这里可以填写实际的模型名称
model_dropdown.pack(pady=5)

# 文件名称输入框
label_file_name = tk.Label(window, text="文件路径（把文件拖入此处）/file path(drop it):")
label_file_name.pack()

# 使用 tk.Text 并设置高度为 5 行
entry_file_name = tk.Text(window, height=4, width=int(30 * scaling_factor))
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

# 输入列数输入框
label_sheet_count = tk.Label(window, text="第几个工作表/sheet number，只输入数字，默认为1（若不知道这是什么，无需修改）")
label_sheet_count.pack()

entry_sheet_count = tk.Text(window, height=2, width=int(30 * scaling_factor))
entry_sheet_count.pack(pady=5)
entry_sheet_count.insert( "1.0", "1")

# 输入列数输入框
label_column_count = tk.Label(window, text="输入作文对应的列数/column(大写，从A列开始)")
label_column_count.pack()

entry_column_count = tk.Text(window, height=2, width=int(30 * scaling_factor))
entry_column_count.pack(pady=5)

# 作文题目输入框（大文本框）
label_essay_title = tk.Label(window, text="需要评分的作文题目/essay prompt")
label_essay_title.pack()

text_essay_title = tk.Text(window, height=7, width=int(30 * scaling_factor))
text_essay_title.pack(pady=5)
text_essay_title.insert(
    "1.0",
    """输入作文题目""",
)


# 评分标准输入框（大文本框）
label_scoring_criteria = tk.Label(window, text="评分标准/grading criteria（默认如下，可修改）")
label_scoring_criteria.pack()

text_scoring_criteria = tk.Text(window, height=9.5, width=int(30 * scaling_factor))
text_scoring_criteria.pack(pady=5)
text_scoring_criteria.insert(
    "1.0",
    """作文评分标准（0-9分，0.5分一档），对每项分别评分（互不影响地评分），
并给出这四项的平均分作为作文的最终总分，四个部分的分数分开给出并分别给出简要点评：
9分为英语母语者，英语文学硕士水平，6.5为中国大学生优秀水平，5.5-6为平均水平。
任务回应：
9：全面深入回应，观点明确。
8：有效回应，表达清晰。
7：全面回应，但有些不够深入。
6：回应基本，但观点不明确。
5：部分完整，未充分展开。
4：回应有限，观点模糊。
3：未有效回应，观点混乱。
2：几乎没有回应，内容无关。
1：没有回应，内容完全不相关。
连贯与衔接：
9：结构清晰，逻辑严谨。
8：合理结构，信息流畅。
7：逻辑清晰，但某些部分流畅性不足。
6：基本结构合理，但存在组织问题。
5：结构简单，缺乏衔接。
4：缺乏连贯性，逻辑混乱。
3：几乎没有连贯性，难以理解。
2：没有结构，内容杂乱无章。
1：完全没有连贯性，无法理解。
词汇多样性：
9：丰富且准确，表达能力强。
8：词汇丰富，少量错误。
7：使用得当，偶有不当或拼写错误。
6：词汇有限，表达清晰但有拼写错误。
5：词汇不足，常见拼写错误。
4：使用不当，影响理解。
3：非常有限，严重影响表达。
2：几乎没有使用恰当词汇。
1：无法使用词汇，无法理解。
语法范围与准确性：
9：准确使用，句子结构多样。
8：良好，少量错误。
7：较好，少量错误不影响理解。
6：基本正确，常有错误影响表达。
5：错误较多，影响理解。
4：错误频繁，影响理解。
3：几乎完全错误，难以理解。
2：没有语法正确的句子。
1：完全没有可识别的语法。""",
)  # 设置默认值

# 提交按钮
submit_button = tk.Button(window, text="提交/Submit", state=tk.DISABLED)  # 默认禁用


# 当用户修改任何输入时启用按钮
def enable_submit(*args):
    submit_button.config(state=tk.NORMAL)


# 绑定输入框的修改事件到 enable_submit
model_var.trace_add("write", enable_submit)
entry_file_name.bind("<KeyRelease>", lambda event: enable_submit())
entry_column_count.bind("<KeyRelease>", lambda event: enable_submit())
text_essay_title.bind("<KeyRelease>", lambda event: enable_submit())
text_scoring_criteria.bind("<KeyRelease>", lambda event: enable_submit())


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

    # 模拟程序处理过程
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
        messagebox.showinfo("结果", f"处理成功。处理后的文件目录： {result}")

    except Exception as e:
        messagebox.showerror("错误", f"处理时出错: {str(e)}")

    finally:
        # 当处理完成后重新启用提交按钮（如果有内容变化的话）
        submit_button.config(state=tk.NORMAL)


# 示例主程序逻辑（你可以用自己的代码替换此部分）
def process_essay(model, file_path, columns, title, criteria, sheet_number):
    if columns == "A" or columns == "1" or columns == "a":
        cols=[0]  # 假设你要读取第1列（A列）
        pass
    elif columns == "B" or columns == "2" or columns == "b":
        cols=[1]  # 假设你要读取第2列（B列）
        pass
    elif columns == "C" or columns == "3" or columns == "c":
        cols=[2]
        pass
    elif columns == "D" or columns == "4" or columns == "d":
        cols=[3]
        pass
    elif columns == "E" or columns == "5" or columns == "e":
        cols=[4]
        pass
    elif columns == "F" or columns == "6" or columns == "f":
        cols=[5]
        pass
    elif columns == "G" or columns == "7" or columns == "g":
        cols=[6]
        pass
    elif columns == "H" or columns == "8" or columns == "h":
        cols=[7]
        pass
    elif columns == "I" or columns == "9" or columns == "i":
        cols=[8]
        pass
    elif columns == "J" or columns == "10" or columns == "j":
        cols=[9]
        pass
    elif columns == "K" or columns == "11" or columns == "k":
        cols=[10]
        pass
    elif columns == "L" or columns == "12" or columns == "l":
        cols=[11]
        pass
    elif columns == "M" or columns == "13" or columns == "m":
        cols=[12]
        pass
    elif columns == "N" or columns == "14" or columns == "n":
        cols=[13]
        pass
    elif columns == "O" or columns == "15" or columns == "o":
        cols=[14]
        pass
    sheet_number = int(sheet_number) - 1
    systemContent = f"""你是一个资深的大学英语教师，有着四十余年的阅卷经验，根据以下作文的题目要求和评分标准，做出评分，分数不要过低但也不要过高，给出少量评语，但无需提供改进建议，不要对文章进行总结，以文本形式给出（不要有markdown标记），以“xx分（总分）：”开头：作文题目: {title}\n评分标准: {criteria}"""
    df = pd.read_excel(file_path)
    def ToArray(file_path, cols, sheet_number):
        # 读取 Excel 文件，指定列和工作表名称
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        FunctionRead = pd.read_excel(file_path, usecols=cols, sheet_name=sheet_names[sheet_number], header=None)
        # 将数据转换为 NumPy 数组
        FunctionArray = np.array(FunctionRead.stack())
        return FunctionArray
    messages_list = ToArray(file_path, cols, sheet_number)
    url = serverUrl  # 指向 Flask 后端
    headers = {"Content-Type": "application/json"}
    responses = []  # 初始化一个空列表来存储响应
    for message in messages_list:
        # print("Message:", message)
        data = {"messages": message, "model": model, "systemContent": systemContent}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_content = (
            response.content.decode("utf-8")
            .replace("\n", "")
            .replace("\r", "")
            .replace(",", "，")
        )
        responses.append(response_content)
        # 打印响应内容
        print("Response content:", response_content)

    input_directory = os.path.dirname(file_path)
    output_file_path = os.path.join(input_directory, "output.csv")
    
    with open(output_file_path, "w", encoding="ANSI") as f:
        for response in responses:
            f.write(response + "\n")
    frequency = 440  # 频率，单位为赫兹
    duration = 1200  # 持续时间 单位为毫秒
    winsound.Beep(frequency, duration)
    return output_file_path


# 提交按钮
submit_button.config(command=submit)
submit_button.pack(pady=20)

# 进入主循环
window.mainloop()
