import json

def get_user_input(prompt, default):
    user_input = input(f"{prompt} (default: {default}, enter -1 or nothing to keep default): ")
    if user_input == "-1" or user_input.strip() == "":
        return default
    return user_input

def initialize_config():
    # 从 config.json 文件中读取默认配置
    # read default configuration from config.json
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)

    if config["frontend"]["language"] == "en":
        config['backend']['api-key'] = get_user_input("Enter API key", config['backend']['api-key'])
        # if you want to add more language options prompt, you can add them below
        config['frontend']['language'] = get_user_input("Enter language(opt: en, zh)", config['frontend']['language'])
        config['backend']['port'] = int(get_user_input("Enter backend port", config['backend']['port']))
        config['frontend']['width_default_value'] = get_user_input("Enter the width of input box", config['frontend']['width_default_value'])
        config['frontend']['serverAddress'] = get_user_input("Enter server address", config['frontend']['serverAddress'])
        config['frontend']['promptFileAddress'] = get_user_input("Enter prompt file address", config['frontend']['promptFileAddress'])
        config['frontend']['rulePlaySettings'] = get_user_input("Enter rule play settings address", config['frontend']['rulePlaySettings'])
        config['frontend']['locale'] = get_user_input("Enter locale", config['frontend']['locale'])
    elif config["frontend"]["language"] == "zh":
        config['backend']['api-key'] = get_user_input("输入API密钥", config['backend']['api-key'])
        config['frontend']['language'] = get_user_input("输入语言(opt: en, zh)", config['frontend']['language'])
        config['backend']['port'] = int(get_user_input("输入后端端口", config['backend']['port']))
        config['frontend']['width_default_value'] = get_user_input("输入输入框宽度", config['frontend']['width_default_value'])
        config['frontend']['serverAddress'] = get_user_input("输入服务器地址", config['frontend']['serverAddress'])
        config['frontend']['promptFileAddress'] = get_user_input("输入提示文件地址", config['frontend']['promptFileAddress'])
        config['frontend']['rulePlaySettings'] = get_user_input("输入规则播放设置地址", config['frontend']['rulePlaySettings'])
        config['frontend']['locale'] = get_user_input("输入区域", config['frontend']['locale'])
    # 保存配置到 config.json 文件
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, ensure_ascii=False, indent=4)

    print("Configuration initialized and saved to config.json")

if __name__ == "__main__":
    initialize_config()