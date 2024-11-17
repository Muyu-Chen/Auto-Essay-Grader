import json
try:
    with open("config.json", "r") as file:
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
language = config.get("frontend", {}).get("language", "zh")

if language == "en":
    Tscoring_criteria = "Scoring criteria"
    Tinstructions = """                          Welcome to the essay grading tool!
    1. Choose the model: max: good performance, high price; 
       plus(recommended); and turbo: poor performance, low price.
    2. Delete the header in the table and keep only the essay 
       content, save it as an xls file (xlsx is not recommended).
    3. Drag the file to the file path and enter the column number 
       corresponding to the essay.
    4. Fill in the essay title and scoring criteria, click submit (and wait).
    5. Open source: https://github.com/Muyu-Chen/Auto-Essay-Grader"""
    TchoosingModel = "Choose the model (default is turbo):"
    TfilePath = "File path (drag the file here)"
    TsheetNumber = "Which sheet, enter a number (no need to modify if you don't know)"
    TcolumnNumber = "The column number corresponding to the essay (uppercase, starting from A)"
    TessayTitle = "Essay writing requirements to be scored"
    TessayTitleExample = """Essay writing requirements to be scored, for example: If you are Li Hua, your art teacher takes you to the park for an art class, please write a letter to Chris, telling him what you did in the park and how you feel."""
    Tsubmit = "Submit"

    Tresult = "Result"
    TresultContent = "Processed successfully. The processed file is saved at: "
    TresultError = "Error"
    TresultErrorReason = "Error occurred during processing: "

elif language == "zh":
    # Chinese
    Tscoring_criteria="评分标准"
    Tinstructions = """                                欢迎使用作文评分工具！
    1. 选择你要使用的模型：max性能好价格高，
    plus最推荐，turbo性能差价格低
    2. 将表格中的表头删除，只保留作文内容，
    然后保存为xls文件（xlsx也可以，但不建议）。
    2. 拖入文件到文件路径，并输入作文对应的列数。
    3. 填写作文题目及评分标准，然后点击提交（随后等待即可）。
    4. 开源地址：https://github.com/Muyu-Chen/Auto-Essay-Grader"""
    TchoosingModel = "选择模型（默认为turbo):"
    TfilePath = "文件路径（把文件拖入此处）"
    TsheetNumber = "第几个工作表，只输入数字，默认为1（若不知道这是什么，无需修改）"
    TcolumnNumber = "输入作文对应的列数(大写，从A列开始)"
    TessayTitle = "需评分的作文写作要求"
    TessayTitleExample = """需要评分的作文写作要求，例如：假如你是李华，你的美术老师带你去公园上了一节美术课，请你写一封信给Chris，告诉他你们在公园里做了什么，你的感受是什么。"""
    Tsubmit = "提交"

    Tresult = "结果"
    TresultContent = "处理成功。处理结果的文件保存在："
    TresultError = "错误"
    TresultErrorReason = "处理时出错："
