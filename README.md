# 英语作文自动评分系统 | Auto-Essay-Grader
**Auto Essay Grader** 是一个基于大语言模型 API 的自动评分工具。上传包含作文的 Excel 文件，其中作文在一列里，然后选择模型，提供作文题目和评分标准，工具就会自动批量生成分数和评语。  
**Auto Essay Grader** is an automated tool for grading essays using language model APIs. Upload an Excel file with essays (in one column), select a model, provide the essay prompt and grading criteria, and the tool will automatically generate scores in bulk.
<div align=center>
<img src="https://github.com/user-attachments/assets/e16b2c78-8a72-4504-9f2c-9fd981e6c295" alt="Image 1" style="width: 32%; margin-right: 5%;  aligen: center">
<img src="https://github.com/user-attachments/assets/a0348b50-6ad5-46b4-a08e-ff66dac8093a" alt="Image 2" style="width: 43%;  aligen: center">    
<p>The left image is the GUI client, the right-side image is the server.</p>
</div>
</div>  


## 功能特性 | Features
**批量作文输入:**  将需要评分的作文内容放入 Excel 文件的同一列，删除表头，让第一排就有内容。  
**模型选择:** 选择所需的语言模型进行评分。  
**自定义作文题目:** 输入作文题目或要求以确保评分的准确性。  
**评分标准:** 根据任务要求，定义评分标准，如任务回应、连贯性、词汇多样性、语法准确性等。  
**自动评分:** 基于大语言模型 API，自动批量为作文评分。  
  
**Bulk Essay Input:** Place the essays that need to be graded into a single column in an Excel file, remove the header, and ensure that the first row contains content.  
**Model Selection:** Choose the language model you want to use for grading.  
**Custom Essay Prompt:** Input the essay prompt to ensure accurate grading.  
**Grading Criteria:** Define grading standards such as task response, coherence, lexical resource, and grammatical accuracy.  
**Automated Grading:** Automatically batch grade essays using a large language model API.  

# 使用方法 | Usage Instruction
### 安装依赖库 | install dependencies  
运行以下指令安装依赖项 | Run the following command to install all the dependencies  
`pip install -r requirements.txt`  

### 配置 | Settings  
打开初始化程序`initialize_config.py`或`initialize_config.exe`，  
按照指令，输入你的通义千问API Key、后端地址、端口等信息。若无需更改，直接按回车即可。  
请注意，如果您对程序一窍不通，可以只输入API-key后，一直按回车即可。  
配置好后，运行后端程序。  
  
Open the initialization program `initialize_config.py` or `initialize_config.exe`,  
follow the instructions, and enter your Qianwen API-Key, backend address, port, and other information. If no changes are needed, simply press Enter.  
Please note, if you are not familiar with the program, you can just enter the API key and keep pressing Enter.  
After configuring, run the backend program.  

### 运行后端和前端 | Run Backend and Frontend Programs
先运行 `server.py` 启动后端服务，然后运行 `GUIClient.py` 启动前端界面。  
或依次运行`server.exe`和`GUIClient.exe`。  
在Linux系统上使用```nohup python3 server.py > EssayJudgemmentOutput.log 2>&1 &```来保存日志。 
  
First, run `server.py` to start the backend service, and then run `GUIClient.py` to launch the frontend interface.  
or run `server.exe` and `GUIClient.exe`.
use ```nohup python3 server.py > EssayJudgemmentOutput.log 2>&1 &``` on Linux to save the log.  

### 准备 Excel 文件：
将需要评分的作文内容存入 Excel 文件中的某一列，并确保删除表头，只保留作文内容（不需要删除其他列）。  
保存文件为 .xls 格式（不建议使用 .xlsx 格式，但程序仍然可以运行）。   
  
Place essays in a single column (do not need delete other columns), remove the header, and save as .xls (or .xlsx, though not recommended).
  
### 选择使用的评分模型 | Select a Model  

| 模型/Model  | 推荐                 | Recommend              |
|:--------:|----------------------|------------------------|
| max   | 性能优异，但价格高      | High performance, but expensive |
| plus  | 最推荐的选项，性价比高 | Most recommended, great value |
| turbo | 性能一般，价格较低    | Lower performance, more affordable |

  
### 导入文件 | Import the File    
将编辑好的 Excel 文件拖入程序指定的文件路径栏中，并输入作文所在的列数。  
Drag the Excel file into the program and enter the essay column number.  
  
### 填写作文题目和评分标准 | Enter Essay Prompt & Grading Criteria  
输入作文的题目和相应的评分标准（如任务回应、连贯性、词汇多样性、语法准确性等）。
Input the essay prompt and grading criteria.  
  
### 提交并评分 | Submit  
点击“提交”按钮，程序将开始自动评分。稍作等待，系统将生成分数并输出结果。  
Click "提交"(means submit) and wait for the scores to be generated.  
   
### 3. 打包成exe方法 | How to package into exe
使用pip安装pyinstaller，`pip install pyinstaller`  
运行`pip show pyinstaller`，打开输出内容显示的“Location”，  
用文本编辑器（例如Windows自带的文本编辑器、vscode等）打开`GUIClient.spec`。  
将Location后的字符串替换掉文件中8-18行的`YOUR FILE PATH`。  
  
若你的系统/目标系统**不是win-x64平台**，使用请打开该路径下的文件夹“tkinterdnd2”，再打开“tkdnd”。  
在这个文件夹中可以看见多个系统版本，选择你电脑/目标电脑的版本（此处我选择`win-x64`）的文件夹打开。  
将这里面的文件路径，替换掉文件中的8-18行的文件路径即可（文件数量不一定一样）。
然后运行`pyinstaller GUIClient.spec`即可。  
    
Use pip to install PyInstaller: `pip install pyinstaller`  
Then, run: `pip show pyinstaller`  
In the output, find and open the "Location" shown using a text editor (e.g., Notepad, VS Code).  
Open the file GUIClient.spec and replace the string in lines 8-18 that says YOUR FILE PATH with the path shown after "Location".  
  
If your system/target system is **not on the win-x64 platform**, go to the folder named "tkinterdnd2" in the Location path, then open the "tkdnd" folder.  
In this folder, you'll see multiple system versions—choose the folder that matches your computer's/target computer's version (for example, I chose win-x64).  
Replace the file paths in lines 8-18 of the .spec file with the corresponding file paths from the selected system version (note that the number of files may vary).    
Finally, run `pyinstaller GUIClient.spec`.

# Todo
## 功能开发
### 短期内计划实现功能  
- [x] 配置文件解耦，脱离主程序
- [x] 拥有初始化应用程序，引导用户更改api-key等设置
- [x] 每30s自动保存文本框中的内容 
- [x] 支持多语言选择
- [ ] 增加结构化输出提示词，保证大模型输出稳定
- [ ] 增加token统计
- [ ] 将评分过程拆开为3步：1. 先让大模型解构题目，分得分点，并让用户确认；2. 用传统方法识别拼写、语法错误，计入得分；3. 将语法错误自动修复（可配置是否修复）后给大模型评分，减少评分误差  
- [ ] 性能优化：使用C#(WIN32 API)重构客户端（即不再适配Mac OS）（Tips. 多久Macbook Air 16+512的价格比我两台Windows加起来价格便宜就可以准备适配了  
- [ ] Windows会显示“未响应”，但是实际软件正在后台运算，通过多线程优化此情况  
  
### 普通功能
- [x] 后台日志输出保存为文件
- [ ] 在每次用户提交操作后，统计使用的资源
- [ ] 优化界面美观程度：添加图标、图片或背景色等，改善视觉效果
- [ ] 作文分自然段段评估、结合原始方法（词汇、语法等）进行评分
- [ ] 自动根据教学大纲出题并评分
- [x] 评分与评语分两列给出
- [ ] 提供深色模式
- [ ] 日志文件输出到文件（而非控制台输出）并定期备份/删除
- [ ] 批量文件处理
- [ ] 在文件处理完成后直接显示统计图
- [ ] 在处理完每一篇论文后自动保存（而不是最后一起写入文档）
- [ ] 增加bug反馈按钮
  
### 商业化功能
- [ ] 后端实现用户增删查改
- [ ] 前端实现用户登录功能
- [ ] 添加用户资料编辑界面
- [ ] 前后端集成支付充值系统
- [ ] 加密软件避免破解
- [ ] 后端实现计费功能，保证前端被破解后也无法调用接口
- [ ] 优化UI界面

### 性能优化
- [ ] 提升应用加载速度：python打包为exe的固有缺陷，使用electron或其他合适技术重写
- [ ] Windows会显示“未响应”，但是实际软件正在后台运算，优化此情况
- [ ] 减少内存占用
- [ ] 减少存储空间占用

### 其他
- [ ] 添加用户协议文档

# 更新日志 | Update
## Nov. 11, 2024
- [x] 配置文件解耦，单独存于json文件中，脱离主程序;
- [x] prompt解耦，单独存于txt文件中，使得程序的应用更广，可以通过更改`criteria.txt`，`rulePlaySettings.txt`来更改默认配置(不建议修改rulePlaySettings);
- [x] 增加初始化程序，让用户一键运行;
- [x] 拥有初始化应用程序，引导用户更改api-key等设置;
- [x] 每30s自动保存文本框中的内容，保存于`criteria.txt`中;
- [x] 初步将文本内容解耦，已建立文件，但目前还没有全部开发完成。
## Nov. 17, 2024  
- [x] 多语言支持  
- [x] 修复部分bug  
- [x] 增加默认prompt使得生成内容的格式更加稳定，避免出现报错  
        
### English Version
- [x] Configuration files decoupled and stored in JSON files, separated from the main program.
- [x] Prompts decoupled and stored in TXT files to make the program more versatile. Changes to `criteria.txt` and `rulePlaySettings.txt` can adjust default settings. Not recommended to change `rulePlaySettings`.
- [x] Added an initialization program for one-click operation.
- [x] Has an initialization app that guides users to change settings like API keys.
- [x] Automatically saves text box content every 30 seconds into `criteria.txt`.
- [x] Text content decoupling started; files created but not fully developed yet.

# 免责声明 | Disclaimer
`icon.ico` 文件是在 2024 年 10 月 16 日使用阿里巴巴通义千问大模型生成的。作者提供了生成所需的提示信息。该文件的版权遵循该公司规定。  
The `icon.ico` file was generated using the Qwen large model by Alibaba on October 16, 2024. The author provided the necessary prompts for its creation. The copyright of this file is subject to the company's terms.
