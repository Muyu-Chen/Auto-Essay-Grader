from flask import Flask, request, jsonify, Response  # Ensure jsonify is imported
from flask_cors import CORS
from openai import OpenAI
import json
from modifyUsers import modifyUserFunc
from checkCardPIN import checkCardPINFunc
from sys import argv
from os import path

DEBUG_MODE=True

# todo: change the directory of the config file
thisDir = path.dirname(path.realpath(argv[0]))
configFile = path.join(thisDir, "config.json")
cardPINFile = path.join(thisDir, "cardPIN.json")
fileLogPath = path.join(thisDir, "fileLog.csv")
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)
api_key_get = config.get("backend", {}).get("api-key", "api-key-error")
api_key_get = str(api_key_get)
port_default = config.get("backend", {}).get("port", "5000")  # Default port
model_default = config.get("backend", {}).get(
    "model", "qwen-plus-0806"
)  # Default model
app = Flask(__name__)

PRICE_LEVEL = 100
PRICE_INPUT_PER_THOUSAND_TURBO = 0.0003 / 1000 * PRICE_LEVEL
PRICE_INPUT_PER_THOUSAND_PLUS = 0.0008 / 1000 * PRICE_LEVEL
PRICE_INPUT_PER_THOUSAND_MAX = 0.02 / 1000 * PRICE_LEVEL

PRICE_OUTPUT_PER_THOUSAND_PLUS = 0.0008 / 1000 * PRICE_LEVEL
PRICE_OUTPUT_PER_THOUSAND_MAX = 0.06 / 1000 * PRICE_LEVEL
PRICE_OUTPUT_PER_THOUSAND_TURBO = 0.0006 / 1000 * PRICE_LEVEL


# THIS IS NOT FOR SAFETY USE.
# YOU SHOULD USE A WHITELIST TO CONTROL ACCESS.
CORS(app, origins="*")  # Allow all origins
# This allows cross-origin requests from any domain, suitable for development purposes.
# Even if origins are restricted to trusted domains, non-browser clients (e.g., bots, scripts)
# can still access the server. CORS only controls browser-based cross-origin requests
# and does not prevent unauthorized or malicious access.
# For better security, implement additional measures like authentication, IP restrictions, or rate limiting.


with app.app_context():
    client = OpenAI(
        api_key=api_key_get,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        userAccount = data.get("userAccount")
        userPassword = data.get("userPassword")
        if (
            userAccount is None
            or userAccount == ""
            or userPassword is None
            or userPassword == ""
        ):
            return jsonify({"error": "手机号或密码不能为空"}), 400
        dataJudgment = {
            "todo": "isVerified",
            "userAccount": userAccount,
            "userPassword": userPassword,
        }
        try:
            returnValue = modifyUserFunc(dataJudgment)
        except Exception as e:
            return jsonify({"error": str(e)}), 501
        if returnValue is None or returnValue == False:
            return jsonify({"error": "账号或密码错误"}), 401
        messages = data.get("messages")
        systemContent = data.get("systemContent")
        model_get = data.get("model")
        if model_get is None or model_get == "":
            model_set = model_default
            print(
                "no model set has been recieved, use default model: " + str(model_set)
            )
        else:
            model_set = model_get
            print("model get is: " + str(model_set))

        if "turbo" in model_set:
            priceInput = PRICE_INPUT_PER_THOUSAND_TURBO
            priceOutput = PRICE_OUTPUT_PER_THOUSAND_TURBO
        elif "plus" in model_set:
            priceInput = PRICE_INPUT_PER_THOUSAND_PLUS
            priceOutput = PRICE_OUTPUT_PER_THOUSAND_PLUS
        else:
            priceInput = PRICE_INPUT_PER_THOUSAND_MAX
            priceOutput = PRICE_OUTPUT_PER_THOUSAND_MAX

        send_message = [
            {
                "role": "system",
                "content": systemContent,
            },
            {
                "role": "user",
                "content": messages,
            },
        ]

        completion = client.chat.completions.create(
            model=model_set,
            messages=send_message,
            stream=False,
            response_format={"type": "json_object"},
        )

        def generate():
            if completion:
                print(completion.model_dump_json())
                print("completed as above")
                # input tokens
                promptTokens = completion.usage.prompt_tokens
                # output tokens
                completionTokens = completion.usage.completion_tokens

                totalPrice = promptTokens * priceInput + completionTokens * priceOutput
                data = {
                    "todo": "findUserField",
                    "field": "currentBalance",
                    "userAccount": userAccount,
                    "userPassword": userPassword,
                }
                # 添加余额显示功能和更新逻辑：在主窗口中显示当前余额，并实现从后端获取余额的功能
                currentBalance = modifyUserFunc(data)
                # 如果不能赊账，就直接返回，把这部分注释去掉
                # 如果允许赊账，就无需修改
                # if currentBalance < totalPrice:
                #    return jsonify({"error": "余额不足"}), 401
                data = {
                    "todo": "addUsage",
                    "userAccount": userAccount,
                    "userPassword": userPassword,
                    "addNum": totalPrice,
                }
                modifyUserFunc(data)
                return completion.choices[0].message.content

        # 调用生成器之前，先判断余额是否足够
        data = {
            "todo": "findUserField",
            "field": "currentBalance",
            "userAccount": userAccount,
            "userPassword": userPassword,
        }
        if modifyUserFunc(data) < 0:
            return jsonify({"error": "余额不足"}), 401

        # print(completion.model_dump_json())
        return Response(generate(), content_type="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    userAccount = data.get("userAccount")
    userPassword = data.get("userPassword")

    if not userAccount or not userPassword:
        return jsonify({"error": "手机号或密码不能为空"}), 400

    data["todo"] = "findUserField"
    data["field"] = "userAccount"
    # Check if user already exists
    existing_user = modifyUserFunc(data)
    # print("is the user existed?:" + str(existing_user))
    if existing_user is not None and existing_user != "":
        return jsonify({"error": "用户已存在"}), 400

    # Register new user
    new_user = {"todo": "addUser", "userAccount": userAccount, "userPassword": userPassword}
    result = modifyUserFunc(new_user)

    if result.get("UID") is not None or result.get("UID") != "":
        return jsonify({"message": "注册成功", "UID": result.get("UID")}), 201
    else:
        return jsonify({"error": "注册失败"}), 503


@app.route("/login", methods=["POST"])
def login():
    dataFromWeb = request.json
    dataFromWeb["todo"] = "isVerified"
    try:
        returnValue = modifyUserFunc(dataFromWeb)
    except Exception as e:
        return jsonify({"error": str(e)}), 504
    if returnValue:
        # token for keep login status
        # dataFromWeb["todo"] = "generateUserTempToken"
        # expirationTime = 24 * 14    # 14 days
        # dataFromWeb["expirationTime"] = expirationTime
        # token = modifyUserFunc(dataFromWeb)
        return (
            jsonify(
                {
                    "message": "登录成功",
                    # "userTempToken": token,
                    # "expirationTime": expirationTime,
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "账号或密码错误"}), 401


@app.route("/charge", methods=["POST"])
def charge():
    data = request.json
    userAccount = data.get("userAccount")
    if userAccount is None or userAccount == "":
        return jsonify({"error": "手机号不能为空"}), 400
    todo = data.get("todo")
    if todo == "getBalance":
        data["todo"] = "findUserField"
        data["field"] = "currentBalance"
        currentBalance = modifyUserFunc(data)
        print("currentBalance: " + str(currentBalance))
        return jsonify({"currentBalance": float(currentBalance)}), 200

    if todo == "charge":
        print("now is in charge")
        cardPIN = data.get("cardPIN")
        if cardPIN is None or cardPIN == "":
            return jsonify({"error": "充值码不能为空"}), 400
        value1, value2, value3 = checkCardPINFunc(cardPIN)
        if value1 == -1:
            return jsonify({"error": "无效：" + str(value2)}), 400
        if value1 == 0 or value1 == 1 or value1 == 2:
            data["todo"] = "findUserField"
            data["field"] = "UID"
            UID = modifyUserFunc(data)
            data["UID"] = UID
            if UID == "" or UID is None:
                print("UID is None")
                return jsonify({"error": "错误 找不到UID"}), 400
            if value1 == 0:
                # only this UID is valid
                if UID != value3:
                    print("UID is not equal to value3")
                    return jsonify({"error": "无效充值码"}), 400
            elif value1 == 1 or value1 == 2:
                # all UIDs are valid
                pass
        else:
            return jsonify({"error": "无效充值码"}), 400
        data["todo"] = "rechargeAccount"
        value2 = int(value2)
        data["addNum"] = value2
        try:
            returnValue = modifyUserFunc(data)
        except Exception as e:
            print("rechargeAccount error" + str(e))
            return jsonify({"error": str(e)}), 505
        if returnValue != 0:  # 不等于原来的余额就是成功
            parsed_price = value2
            # delete the card PIN from the database
            with open("cardPIN.json", "r") as f:
                data = json.load(f)
            dataPrice = data.get(str(parsed_price))
            # Assume price_level is the price level you determined earlier
            if dataPrice:
                for pin in dataPrice:
                    if pin == cardPIN:
                        value2 = 0
                        # delete the card PIN from the database
                        dataPrice.remove(pin)
                        data[str(parsed_price)] = dataPrice
                        with open("cardPIN.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                        break
            return jsonify({"message": "充值成功"}), 200
        else:
            return jsonify({"error": "充值失败"}), 506


@app.route("/getData", methods=["POST"])
def getData():
    data = request.json
    todo = data.get("todo")
    filed = data.get("field")
    if DEBUG_MODE:
        print("Now is in server.getData. todo: " + str(todo))
    UID = data.get("UID")
    if UID == "" or UID is None or UID == "None":
        userAccount = data.get("userAccount")
        if DEBUG_MODE:
            print("userAccount: " + str(userAccount))
        if userAccount is None or userAccount == "" or userAccount == "None":
            return jsonify({"error": "用户名不能为空"}), 400
        else:
            data["todo"] = "findUserField"
            data["field"] = "UID"
            try:
                UID = modifyUserFunc(data)
            except Exception as e:
                print("getData error: " + str(e))
                return jsonify({"error": str(e)}), 400
            if UID == "" or UID is None:
                return jsonify({"error": "找不到用户"}), 400
        data["UID"] = UID
        data["todo"] = todo
        data["field"] = filed

    if todo == "getBalance":
        data["todo"] = "findUserField"
        data["field"] = "currentBalance"
        try:
            currentBalance = modifyUserFunc(data)
        except Exception as e:
            print("getBalance error: " + str(e))
            return jsonify({"error": str(e)}), 400
        return jsonify({"currentBalance": float(currentBalance)}), 200
    if todo == "getData":
        data["todo"] = "findUserField"
        data["field"] = "userName"
        try:
            userName = modifyUserFunc(data)
            data["field"] = "currentBalance"
            currentBalance = modifyUserFunc(data)
            data["field"] = "userAccount"
            userAccount = modifyUserFunc(data)
            data["field"] = "email"
            email = modifyUserFunc(data)
            data["field"] = "personalBio"
            personalBio = modifyUserFunc(data)
            data["field"] = "phoneNumber"
            phoneNumber = modifyUserFunc(data)
        except Exception as e:
            print("getData error: " + str(e))
            return jsonify({"error": str(e)}), 400
        return (
            jsonify(
                {
                    "userName": userName,
                    "currentBalance": float(currentBalance),
                    "UID": UID,
                    "userAccount": userAccount,
                    "email": email,
                    "personalBio": personalBio,
                    "phoneNumber": phoneNumber,
                }
            ),
            200,
        )
    return jsonify({"error": "未知操作"}), 402


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_default)
