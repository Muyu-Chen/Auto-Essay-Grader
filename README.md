# 英语作文自动评分系统 | Auto-Essay-Grader
**Auto Essay Grader** 是一个基于大语言模型 API 的自动评分工具。上传包含作文的 Excel 文件，其中作文在一列里，然后选择模型，提供作文题目和评分标准，工具就会自动批量生成分数和评语。  
**Auto Essay Grader** is an automated tool for grading essays using language model APIs. Upload an Excel file with essays (in one column), select a model, provide the essay prompt and grading criteria, and the tool will automatically generate scores in bulk.

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

### 运行后端和前端 | Run Backend and Frontend Programs
先运行 `server.py` 启动后端服务，然后运行 `GUIClient.py` 启动前端界面。
First, run `server.py` to start the backend service, and then run `GUIClient.py` to launch the frontend interface.  

### 准备 Excel 文件：
将需要评分的作文内容存入 Excel 文件中的某一列，并确保删除表头，只保留作文内容（不需要删除其他列）。  
保存文件为 .xls 格式（不建议使用 .xlsx 格式，但程序仍然可以运行）。 
Place essays in a single column (do not need delete other columns), remove the header, and save as .xls (or .xlsx, though not recommended).

### 选择使用的评分模型 | Select a Model  
max：性能好，但价格高 | High performance, expensive.  
plus：最推荐的选项，性价比高 | Recommended.  
turbo：性能较差，价格较低 | Low performance, cheaper.  

### 导入文件 | Import the File    
将编辑好的 Excel 文件拖入程序指定的文件路径栏中，并输入作文所在的列数。  
Drag the Excel file into the program and enter the essay column number.  

### 填写作文题目和评分标准 | Enter Essay Prompt & Grading Criteria  
输入作文的题目和相应的评分标准（如任务回应、连贯性、词汇多样性、语法准确性等）。
Input the essay prompt and grading criteria.  

### 提交并评分 | Submit  
点击“提交”按钮，程序将开始自动评分。稍作等待，系统将生成分数并输出结果。  
Click "提交"(means submit) and wait for the scores to be generated.  

# 配置方法 | Settings  
### 1. 后端设置 | Backend Setting  
  打开后端 Python 文件`server.py`，  
  找到调用大语言模型 API 的代码部分`line：14`。
  将`sk-xxx`替换为你的通义千问API Key。  
  `line14: api_key="sk-xxx", # Replace with your API key`  
  端口设置在`line5: port_default = 5000  # Default port` ，除非您已使用该端口，否则无需修改。
  如果想使用open AI的 API，请删除15行的base_url，更改10行的模型名称，并按照open AI的API说明更改48行的返回内容。  
配置好后，运行后端程序。  
  Open the backend Python file `server.py`,  
  and locate the section that calls the large language model API at `line: 14`.  
  Replace `sk-xxx` with your Tongyi Qwen API Key.  
  `line 14: api_key="sk-xxx", # Replace with your API key`  
  Port setting located at `line5: port_default = 5000  # Default port`, otherwise you had already use this port, do not have to change it.
  If you need to use OpenAI's ChatGPT key, simply remove line 15 which sets the base_url. Additionally, make sure to change the model name to the appropriate one for your API. Also, update line 48 to modify the return content according to OpenAI's official documentation.  
  After configuring, run the backend program.

### 2. 前端设置 | Frontend Settings  
打开前端程序，将`line14`处地址修改为你自己的后端服务器地址。  
`serverUrl="http://localhost:5000/chat" # follow the format of "http://ip:port/chat"`  
默认连接本地的5000端口，若后端除了加上了API key以外没有做任何修改，并且运行在本地服务器，则此处也无需修改。  
Open the frontend program and modify the address at line 14 to point to your own backend server address.  
`serverUrl="http://localhost:5000/chat" # follow the format of "http://ip:port/chat"`    
By default, it connects to the local server on port 5000. If the backend has not been modified beyond adding the API key and is running on the local server, you do not need to change this.  
  
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
### 普通功能
- [ ] 在每次用户提交操作后，统计使用的资源
- [ ] 优化界面美观程度
- [ ] 添加图标、图片或背景色等，改善视觉效果
- [ ] 作文分段评估、结合原始方法（词汇、语法等）进行评分
- [ ] 评分与评语分两列给出（给出用户选项）
- [ ] 提供深色模式
- [ ] 日志文件单独输出（而非控制台输出）
- [ ] 批量文件处理
- [ ] 在文件处理完成后直接显示统计图
- [ ] 在处理完每一篇论文后自动保存（而不是最后一起写入文档）
- [ ] 增加bug反馈按钮
  
### 商业化功能
- [ ] 后端实现用户增删查改
- [ ] 前端实现用户登录功能
- [ ] 添加用户资料编辑界面
- [ ] 前后端集成支付充值系统

### 性能优化
- [ ] 提升应用加载速度
- [ ] Windows会显示“未响应”，但是实际软件正在后台运算，优化此情况
- [ ] 减少内存占用
- [ ] 减少存储空间占用

### 其他
- [ ] 添加用户协议文档

