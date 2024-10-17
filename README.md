# 英语作文自动评分系统 / Auto-Essay-Grader
Auto Essay Grader 是一个基于大语言模型 API 的自动评分工具。上传包含作文的 Excel 文件，其中作文在一列里，然后选择模型，提供作文题目和评分标准，工具就会自动批量生成分数和评语。  
Auto Essay Grader is an automated tool for grading essays using language model APIs. Upload an Excel file with essays (in one column), select a model, provide the essay prompt and grading criteria, and the tool will automatically generate scores in bulk.

功能特性
批量作文输入：将需要评分的作文内容放入 Excel 文件的同一列。
模型选择：选择所需的语言模型进行评分。
自定义作文题目：输入作文题目或要求以确保评分的准确性。
评分标准：根据任务要求，定义评分标准，如任务回应、连贯性、词汇多样性、语法准确性等。
自动评分：基于大语言模型 API，自动批量为作文评分。
使用方法
1. 后端设置
打开后端 Python 文件，找到调用大语言模型 API 的代码部分。
将你的 通义千问 API Key 填写在合适位置。
python
复制代码
# 示例代码片段
api_key = "你的通义千问 API Key"
配置好后，运行后端程序。
2. 前端设置
打开前端程序，找到指向后端地址的部分，将该地址修改为你自己的后端服务器地址。
javascript
复制代码
// 示例代码片段
const backendUrl = "你的后端服务器地址";
保存修改并运行前端程序。
示例
将需要评分的作文存入 Excel 文件的某一列。
拖动 Excel 文件到程序中。
选择评分模型、填写作文题目和评分标准。
开始自动评分，系统将生成分数并输出结果。
