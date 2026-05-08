from datetime import datetime
import hashlib
import json
import threading
from os import makedirs, name, path

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from werkzeug.utils import secure_filename

from checkCardPIN import checkCardPINFunc
from modifyUsers import modifyUserFunc
from processEssay import process_essay_from_web

DEBUG_MODE = name == "nt"

BASE_DIR = path.dirname(path.abspath(__file__))
ROOT_DIR = path.dirname(BASE_DIR)
SRC_DIR = path.join(ROOT_DIR, "src")
CLIENT_DIR = path.join(ROOT_DIR, "client")

CONFIG_FILE = path.join(SRC_DIR, "config.json")
CARD_PIN_FILE = path.join(SRC_DIR, "cardPIN.json")
FIRST_PROMPT_PATH = path.join(CLIENT_DIR, "firstPrompt.txt")
RULE_PLAY_SETTINGS_PATH = path.join(CLIENT_DIR, "rulePlaySettings.txt")
ESSAY_CRITERIA_PATH = path.join(CLIENT_DIR, "criteria.txt")
UPLOAD_FOLDER = path.join(BASE_DIR, "uploads")
MAX_CONTENT_SIZE = 5 * 1024 * 1024

makedirs(UPLOAD_FOLDER, exist_ok=True)

with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    config = json.load(file)

api_key_get = str(config.get("backend", {}).get("api-key", "api-key-error"))
port_default = int(config.get("backend", {}).get("port", 5000))
model_default = config.get("backend", {}).get("model", "qwen-plus")

PRICE_INPUT_PER_THOUSAND_TURBO = 0.0003 / 1000
PRICE_INPUT_PER_THOUSAND_PLUS = 0.0008 / 1000
PRICE_INPUT_PER_THOUSAND_MAX = 0.02 / 1000
PRICE_OUTPUT_PER_THOUSAND_TURBO = 0.0006 / 1000
PRICE_OUTPUT_PER_THOUSAND_PLUS = 0.002 / 1000
PRICE_OUTPUT_PER_THOUSAND_MAX = 0.06 / 1000

app = Flask(__name__)
CORS(app)

with app.app_context():
    client = OpenAI(
        api_key=api_key_get,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


def process_essay_thread(
    model,
    filepath_name,
    columns,
    essay_prompt,
    essay_criteria,
    sheet_number,
    user_account,
    user_password,
    rule_play_settings,
    system_prompt_first,
    output_csv_name,
    log_csv_name,
    default_cri,
):
    process_essay_from_web(
        model,
        filepath_name,
        columns,
        essay_prompt,
        essay_criteria,
        sheet_number,
        user_account,
        user_password,
        rule_play_settings,
        system_prompt_first,
        output_csv_name,
        log_csv_name,
        default_cri,
    )


def get_user_uid(user_account, user_password=None):
    data = {
        "todo": "findUserField",
        "field": "UID",
        "userAccount": user_account,
    }
    if user_password:
        data["userPassword"] = user_password
    return str(modifyUserFunc(data))


def verify_user_credentials(user_account, user_password, version=None, is_login=False):
    data = {
        "todo": "isVerified",
        "userAccount": user_account,
        "userPassword": user_password,
        "isLogin": "true" if is_login else "false",
    }
    if version:
        data["version"] = version
    return modifyUserFunc(data)


def get_price_rates(model_name, price_level):
    if "turbo" in model_name:
        return (
            PRICE_INPUT_PER_THOUSAND_TURBO * price_level,
            PRICE_OUTPUT_PER_THOUSAND_TURBO * price_level,
        )
    if "plus" in model_name:
        return (
            PRICE_INPUT_PER_THOUSAND_PLUS * price_level,
            PRICE_OUTPUT_PER_THOUSAND_PLUS * price_level,
        )
    return (
        PRICE_INPUT_PER_THOUSAND_MAX * price_level,
        PRICE_OUTPUT_PER_THOUSAND_MAX * price_level,
    )


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        user_account = data.get("userAccount")
        user_password = data.get("userPassword")
        json_or_not = data.get("jsonOrNot")

        if not user_account or not user_password:
            return jsonify({"error": "手机号或密码不能为空"}), 400

        try:
            is_verified = verify_user_credentials(user_account, user_password)
        except Exception as e:
            return jsonify({"error": str(e)}), 501

        if is_verified == -1:
            return jsonify({"error": "找不到用户"}), 400
        if not is_verified:
            return jsonify({"error": "账号或密码错误"}), 401

        messages = data.get("messages")
        system_content = data.get("systemContent")
        model_set = data.get("model") or model_default

        try:
            price_level = modifyUserFunc(
                {
                    "todo": "findUserField",
                    "field": "priceLevel",
                    "userAccount": user_account,
                    "userPassword": user_password,
                }
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 501

        if price_level in (None, "", "None"):
            price_level = 100

        price_input, price_output = get_price_rates(model_set, float(price_level))
        send_message = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": messages},
        ]

        if json_or_not == "true":
            completion = client.chat.completions.create(
                model=model_set,
                messages=send_message,
                stream=False,
                response_format={"type": "json_object"},
                top_p=0.3,
                temperature=0.7,
            )
        else:
            completion = client.chat.completions.create(
                model=model_set,
                messages=send_message,
                stream=False,
            )

        def generate():
            prompt_tokens = completion.usage.prompt_tokens
            completion_tokens = completion.usage.completion_tokens
            total_price = prompt_tokens * price_input + completion_tokens * price_output

            current_balance = modifyUserFunc(
                {
                    "todo": "findUserField",
                    "field": "currentBalance",
                    "userAccount": user_account,
                    "userPassword": user_password,
                }
            )
            if current_balance is not None and current_balance < 0:
                return jsonify({"error": "余额不足"}), 401

            modifyUserFunc(
                {
                    "todo": "addUsage",
                    "userAccount": user_account,
                    "userPassword": user_password,
                    "addNum": total_price,
                }
            )
            return completion.choices[0].message.content

        current_balance = modifyUserFunc(
            {
                "todo": "findUserField",
                "field": "currentBalance",
                "userAccount": user_account,
                "userPassword": user_password,
            }
        )
        if current_balance < 0:
            return jsonify({"error": "余额不足"}), 401

        return Response(generate(), content_type="text/plain")
    except Exception as e:
        print("chat error:", e)
        return jsonify({"error": str(e)}), 502


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    user_account = data.get("userAccount")
    user_password = data.get("userPassword")
    referred_by_uid = str(data.get("referredByUID") or "0")

    if not user_account or not user_password:
        return jsonify({"error": "手机号或密码不能为空"}), 400

    try:
        modifyUserFunc(
            {
                "todo": "findUserField",
                "field": "userAccount",
                "userAccount": user_account,
            }
        )
        return jsonify({"error": "用户已存在"}), 400
    except Exception as e:
        if str(e) != "no such user":
            return jsonify({"error": str(e)}), 500

    result = modifyUserFunc(
        {
            "todo": "addUser",
            "userAccount": user_account,
            "userPassword": user_password,
            "referredByUID": referred_by_uid,
        }
    )

    if result.get("UID"):
        return jsonify({"message": "注册成功", "UID": result.get("UID")}), 201
    return jsonify({"error": "注册失败"}), 503


@app.route("/login", methods=["POST"])
def login():
    data_from_web = request.get_json(silent=True) or {}
    data_from_web["todo"] = "isVerified"

    try:
        return_value = modifyUserFunc(data_from_web)
    except Exception as e:
        print("login error:", e)
        if str(e) == "no such user":
            return jsonify({"error": "no such user"}), 504
        return jsonify({"error": str(e)}), 504

    if return_value == -1:
        return jsonify({"error": "no such user"}), 504
    if return_value:
        return jsonify({"message": "登录成功"}), 200
    return jsonify({"error": "账号或密码错误"}), 401


@app.route("/charge", methods=["POST"])
def charge():
    data = request.get_json(silent=True) or {}
    user_account = data.get("userAccount")
    if not user_account:
        return jsonify({"error": "手机号不能为空"}), 400

    todo = data.get("todo")
    if todo != "charge":
        return jsonify({"error": "未知操作"}), 402

    card_pin = data.get("cardPIN")
    if not card_pin:
        return jsonify({"error": "充值码不能为空"}), 400

    value1, value2, value3 = checkCardPINFunc(card_pin)
    if value1 == -1:
        return jsonify({"error": "无效：" + str(value2)}), 400

    data["todo"] = "findUserField"
    data["field"] = "UID"
    try:
        uid = modifyUserFunc(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if not uid:
        return jsonify({"error": "错误 找不到UID"}), 400

    data["UID"] = uid
    if value1 == 0 and uid != value3:
        return jsonify({"error": "无效充值码"}), 400

    data["todo"] = "rechargeAccount"
    data["addNum"] = int(value2)
    try:
        return_value = modifyUserFunc(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 505

    if return_value == 0:
        return jsonify({"error": "充值失败"}), 506

    parsed_price = int(value2)
    with open(CARD_PIN_FILE, "r", encoding="utf-8") as f:
        card_pin_data = json.load(f)
    pins = card_pin_data.get(str(parsed_price), [])
    if card_pin in pins:
        pins.remove(card_pin)
        card_pin_data[str(parsed_price)] = pins
        with open(CARD_PIN_FILE, "w", encoding="utf-8") as f:
            json.dump(card_pin_data, f, ensure_ascii=False, indent=4)
    return jsonify({"message": "充值成功"}), 200


@app.route("/getData", methods=["GET", "POST"])
def get_data():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
    else:
        data = request.args.to_dict()

    todo = data.get("todo")
    field = data.get("field")
    uid = data.get("UID")
    user_account = data.get("userAccount")

    if not uid:
        if not user_account:
            return jsonify({"error": "用户名不能为空"}), 400
        try:
            uid = get_user_uid(user_account, data.get("userPassword"))
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        if not uid:
            return jsonify({"error": "找不到用户"}), 400

    base_data = {
        "UID": uid,
        "userAccount": user_account,
        "userPassword": data.get("userPassword"),
    }

    if todo == "getBalance":
        try:
            current_balance = modifyUserFunc(
                {**base_data, "todo": "findUserField", "field": "currentBalance"}
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        return jsonify({"currentBalance": float(current_balance)}), 200

    if todo == "getData":
        try:
            user_name = modifyUserFunc(
                {**base_data, "todo": "findUserField", "field": "userName"}
            )
            current_balance = modifyUserFunc(
                {**base_data, "todo": "findUserField", "field": "currentBalance"}
            )
            account = modifyUserFunc(
                {**base_data, "todo": "findUserField", "field": "userAccount"}
            )
            email = modifyUserFunc(
                {**base_data, "todo": "findUserField", "field": "email"}
            )
            personal_bio = modifyUserFunc(
                {**base_data, "todo": "findUserField", "field": "personalBio"}
            )
            phone_number = modifyUserFunc(
                {**base_data, "todo": "findUserField", "field": "phoneNumber"}
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        return (
            jsonify(
                {
                    "userName": user_name,
                    "currentBalance": float(current_balance),
                    "UID": uid,
                    "userAccount": account,
                    "email": email,
                    "personalBio": personal_bio,
                    "phoneNumber": phone_number,
                }
            ),
            200,
        )

    if todo == "setData":
        try:
            return_value = modifyUserFunc(
                {
                    **base_data,
                    "todo": "updateUser",
                    "field": field,
                    "newValue": data.get("newValue"),
                }
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        if return_value != 200:
            return jsonify({"error": "更新失败"}), 400
        return jsonify({"message": "更新成功"}), 200

    if todo == "isProcessing":
        user_dir = path.join(UPLOAD_FOLDER, uid)
        makedirs(user_dir, exist_ok=True)
        processing_file = path.join(user_dir, "isProcessing.txt")
        if not path.exists(processing_file):
            return jsonify({"isProcessing": "false"}), 200
        try:
            with open(processing_file, "r", encoding="utf-8") as file:
                is_processing = file.read()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        return jsonify({"isProcessing": is_processing}), 200

    return jsonify({"error": "未知操作"}), 402


@app.route("/uploads/<uid>/<filename>", methods=["GET"])
def download_upload(uid, filename):
    safe_uid = secure_filename(uid)
    safe_filename = secure_filename(filename)
    return send_from_directory(
        path.join(UPLOAD_FOLDER, safe_uid),
        safe_filename,
        as_attachment=True,
    )


@app.route("/upload", methods=["POST"])
def upload_file():
    allowed_extensions = {"csv", "xls", "xlsx"}

    def allowed_file(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

    if request.content_length and request.content_length > MAX_CONTENT_SIZE:
        return jsonify({"error": "File size exceeds the maximum limit."}), 413
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 401

    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify({"error": "No selected file"}), 402

    user_account = request.form.get("userAccount")
    user_password = request.form.get("userPassword")
    if not user_account or not user_password:
        return jsonify({"error": "用户名或密码不能为空"}), 400

    try:
        uid = get_user_uid(user_account, user_password)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if not uid:
        return jsonify({"error": "找不到用户"}), 400

    try:
        is_verified = verify_user_credentials(user_account, user_password, is_login=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if not is_verified:
        return jsonify({"error": "账号或密码错误"}), 401

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type or file size exceeds the limit."}), 400

    file_name, file_extension = path.splitext(file.filename)
    if not file_name or not file_extension:
        return jsonify({"error": "file name cannot be none"}), 400

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    hashed_name = hashlib.md5((file_name + timestamp).encode()).hexdigest()
    stored_filename = secure_filename(f"upload_{hashed_name}{file_extension.lower()}")

    user_dir = path.join(UPLOAD_FOLDER, uid)
    makedirs(user_dir, exist_ok=True)
    file_path = path.join(user_dir, stored_filename)

    log_file_path = path.join(user_dir, secure_filename(f"{uid}_File_Log.csv"))
    if not path.exists(log_file_path):
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            log_file.write("UserAccount,UID,fileName,timeStamp,hashedFileName\n")
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{user_account},{uid},{file_name},{timestamp},{stored_filename}\n")

    file.save(file_path)
    return (
        jsonify(
            {
                "message": f"File {stored_filename} has been uploaded successfully.",
                "fileID": stored_filename,
                "fileIDName": hashed_name,
            }
        ),
        200,
    )


@app.route("/process", methods=["POST"])
def process_file():
    data_from_web = request.get_json(silent=True) or {}
    file_id = data_from_web.get("fileID")
    file_full_name = data_from_web.get("fileFullName")
    user_account = data_from_web.get("userAccount")
    user_password = data_from_web.get("userPassword")
    essay_prompt = data_from_web.get("essayPrompt")
    essay_criteria = data_from_web.get("essayCriteria")
    sheet_number = data_from_web.get("sheetName")
    columns = data_from_web.get("colName")
    model = data_from_web.get("model") or model_default

    if not file_id:
        return jsonify({"error": "fileID不能为空"}), 400
    if not user_account:
        return jsonify({"error": "用户名不能为空"}), 400
    if not user_password:
        return jsonify({"error": "密码不能为空"}), 400

    try:
        uid = get_user_uid(user_account, user_password)
        is_verified = verify_user_credentials(user_account, user_password, is_login=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if not is_verified:
        return jsonify({"error": "账号或密码错误"}), 401

    with open(FIRST_PROMPT_PATH, "r", encoding="utf-8") as file:
        system_prompt_first = file.read()
    with open(RULE_PLAY_SETTINGS_PATH, "r", encoding="utf-8") as file:
        rule_play_settings = file.read()

    default_cri = False
    if not essay_criteria or essay_criteria == "None":
        with open(ESSAY_CRITERIA_PATH, "r", encoding="utf-8") as file:
            essay_criteria = file.read()
        default_cri = True

    user_dir = path.join(UPLOAD_FOLDER, uid)
    makedirs(user_dir, exist_ok=True)
    processing_file = path.join(user_dir, "isProcessing.txt")
    with open(processing_file, "w", encoding="utf-8") as file:
        file.write("true")

    output_csv_name = path.join(user_dir, f"output_{file_id}.csv")
    log_csv_name = path.join(user_dir, f"log_{file_id}.csv")
    file_path = path.join(user_dir, file_full_name)

    thread = threading.Thread(
        target=process_essay_thread,
        args=(
            model,
            file_path,
            columns,
            essay_prompt,
            essay_criteria,
            sheet_number,
            user_account,
            user_password,
            rule_play_settings,
            system_prompt_first,
            output_csv_name,
            log_csv_name,
            default_cri,
        ),
        daemon=True,
    )
    thread.start()
    return jsonify({"message": "文件正在处理ing"}), 200


@app.route("/checkStatus", methods=["GET"])
def check_status():
    user_account = request.args.get("userAccount")
    file_id = request.args.get("fileID")

    if not user_account:
        return jsonify({"error": "用户名不能为空 checkStatus"}), 400
    if not file_id:
        return jsonify({"error": "fileID不能为空 checkStatus"}), 400

    try:
        uid = get_user_uid(user_account)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if not uid:
        return jsonify({"error": "找不到用户 checkStatus"}), 400

    user_dir = path.join(UPLOAD_FOLDER, uid)
    makedirs(user_dir, exist_ok=True)
    processing_file = path.join(user_dir, "isProcessing.txt")

    if not path.exists(processing_file):
        return jsonify({"isProcessing": "false"}), 200

    with open(processing_file, "r", encoding="utf-8") as file:
        is_processing = file.read()

    if is_processing == "true":
        return jsonify({"complete": "false"}), 200

    download_link = request.host_url.rstrip("/") + f"/uploads/{uid}/output_{file_id}.csv"
    return jsonify({"complete": "true", "downloadLink": download_link}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_default)
