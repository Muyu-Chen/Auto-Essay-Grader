import requests
import json
import pandas as pd
import numpy as np
from os import path
import openpyxl
import xlrd
from time import sleep

BASE_DIR = path.dirname(path.abspath(__file__))
CONFIG_FILE = path.join(BASE_DIR, "..", "src", "config.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    CONFIG = json.load(file)

SERVER_ADDRESS = CONFIG.get("frontend", {}).get("serverAddress", "http://127.0.0.1")
BACKEND_PORT = str(CONFIG.get("backend", {}).get("port", "5000"))

def process_essay_from_web(
    model, # 第三次的模型
    file_path, # 作文文件路径（具体到文件）
    columns, # 作文所在列
    title, # 作文题目
    criteria, # 评分标准
    sheet_number, # 作文所在工作表
    userAccount, # 用户账号
    userPassword, # 用户密码
    rulePlaySettings, # 评分规则
    systemPromptFirst, # 第一次的提示 string
    outputcsvName, # 输出文件名，名称即可，不需要路径
    logcsvName, # 日志文件名
    defaultCri, # 是不是默认的cri
):
    print("\n---going into processEssay.py file---\n")
    ruleOutputFormat = """**输出格式**：
    - 使用JSON格式输出，包含以下两个键：
    - `comment`：对每个评分维度的简要评语，说明评分分值、扣分多少和理由。
    - `totalGrade`：计算所有维度分值和。
    必须包含、且仅包含键comment和totalGrade."""

    serverUrl = "".join([SERVER_ADDRESS, ":", BACKEND_PORT, "/chat"])

    modelFirst = "qwen-plus"  # 对作文进行问题识别
    modelSecond = "qwen-plus"  # 检查问题识别的结果
    # modelThird # 对作文进行分项评分，需要用户输入
    modelForth = "qwen-plus"
    # 处理列号
    col_map = {chr(65 + i): i for i in range(26)}  # A-Z 映射到 0-25
    col_map.update({chr(97 + i): i for i in range(26)})  # a-z 映射到 0-25
    col_map.update({str(i + 1): i for i in range(26)})  # 1-26 映射到 0-25
    cols = [col_map[columns]] if columns in col_map else None
    if cols is None:
        raise ValueError("无效的列标识")
    sheet_number = int(sheet_number) - 1  # 转为索引

    systemContentFirst = systemPromptFirst
    systemContentSecond = systemContentFirst
    systemContentThird = f"""{rulePlaySettings}\n 需评分的作文写作要求:“ {title}”\n评分标准: {criteria}。"""

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

    input_directory = path.dirname(file_path)
    output_file_path = path.join(input_directory, outputcsvName)
    output_file_path_log = path.join(input_directory, logcsvName)
    filepathNameIsProcessing = path.join(input_directory, "isProcessing.txt")
    # 清空文件内容，添加表头
    try:

        with open(output_file_path, "w", encoding="utf-8-sig") as f:
            f.write("Grade, Comment\n")

        with open(output_file_path_log, "w", encoding="utf-8-sig") as f:
            f.write(
                "第一轮输出（指出作文存在的问题）,第二轮输出（在第一轮的基础上再次确认问题）,第三轮输出（前两轮的基础上输出评分）,\n"
            )
    except Exception as e:
        print(f"An error occurred: {e}")
        output_file_path = path.join(input_directory, "2."+outputcsvName)
        output_file_path_log = path.join(input_directory, "2."+logcsvName)
        try:
            with open(output_file_path, "w", encoding="utf-8-sig") as f:
                f.write("Grade, Comment\n")
            with open(output_file_path_log, "w", encoding="utf-8-sig") as f:
                f.write(
                    "第一轮输出（指出作文存在的问题）,第二轮输出（在第一轮的基础上再次确认问题）,第三轮输出（前两轮的基础上输出评分）,\n"
                )
        except Exception as e:
            return "Error: " + str(e)
    try:
        for message in messages_list:
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
                        responseFirst_content.replace(",", "，")
                        .replace("\n", " ")
                        .replace("\r", " ")
                        + ","
                    )
            except Exception as e:
                print("Error: 第一轮日志输出错误： " + str(e))
            print("before 2nd")
            secondTimeMessage = f"""{firstTimeMessage} **assistant:** \n第一部分文章评分结果: \n{responseFirst_content}. 请再次全面识别问题，检查其中是否有不符合原文的虚假错误信息，如果有，请删除该错误信息；若有遗漏，请补充完整。并按照上文提及的输出要求，根据评分标准{criteria}，再次输出点评。"""
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
                        + ","
                    )
            except Exception as e:
                print("Error: 第二轮日志输出错误： " + str(e))
            print("——————————\n第二部分：\n" + response_content)

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
            if not defaultCri:
                criteriaForth = criteria
            else:
                criteriaForth = (
                    "每项评分维度各占10分，总分为50分。每项评分维度满分各10分，累计总分为50分。"
                )
            forthTime = {
                "messages": f"""请结合评分标准,{criteriaForth}。\n请根据以下评分的“分项评分总结”，对文章的评分进行计算（请注意，不计算评分维度内单独写的扣分）。结合文章中的分数计算总分。用JSON格式输出，包含以下两个键：
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
            responseNew = f"{grade}, {comment}"
            responses.append(responseNew)

            print("————————————————————— the processed response —————————————————————")
            print(
                "(验证是否正确提取成绩) Response content: \n"
                + (grade + ", " + comment)[:40]
            )
            try:
                with open(output_file_path, "a", encoding="utf-8-sig") as f:
                    f.write(responseNew + "\n")
            except Exception as e:
                sleep(3)
                try:
                    with open(output_file_path, "a", encoding="utf-8-sig") as f:
                        f.write(responseNew + "\n")
                except Exception as e:
                    sleep(3)
                    try:
                        with open(output_file_path, "a", encoding="utf-8-sig") as f:
                            f.write(responseNew + "\n")
                    except Exception as e:
                        return "Error: " + str(e)
            print("—————————————————————————————passage end—————————————————————————————\n")
        return output_file_path
    finally:
        with open(filepathNameIsProcessing, "w", encoding="utf-8") as f:
            f.write("false")
