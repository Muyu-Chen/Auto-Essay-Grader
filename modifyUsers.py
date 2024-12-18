import json
from datetime import datetime
import hashlib

with open('userData.json', 'r', encoding='utf-8') as file:
    userData = json.load(file)

def createUser(data):
    print("Now is in addUserFunction")
    userName = data.get("userName")
    userPassword = data.get("userPassword")
    userPhone = data.get("userPhone")
    current_time = datetime.now()
    creating_date = current_time.strftime("%Y%m%d")  # "20241217"
    creating_time = current_time.strftime("%H%M%S")  # "120821"
    userPassword = hashPassword(userPassword,creating_date, creating_time)
    # 遍历找最大的 UID
    max_uid = 0
    for user in userData["users"]:
        try:
            max_uid = max(max_uid, int(user["UID"]))
        except ValueError:
            continue
    new_uid = str(max_uid + 1)
    new_user = {
        "UID": new_uid,
        "userName": userName,
        "userPhone": userPhone,
        "userPassword": userPassword,
        "creatingDate": creating_date,
        "creatingTime": creating_time,
        "totalDeposit": 0,
        "totalUsed": 0,
        "currentBalance": 0
    }
    userData["users"].append(new_user)
    with open('userData.json', 'w', encoding='utf-8') as file:
        json.dump(userData, file, ensure_ascii=False, indent=4)
    print(f"新用户 {userName} 创建成功，UID 为 {new_uid}。")

def rechargeAccount(data, UID, addNum):
    UID=str(UID)
    totalDeposite = getUserInfo(UID, "totalDeposite") + addNum
    setUserInfo(UID, "totalDeposite", totalDeposite)
    # totalUsed = getUserInfo(UID, "totalUsed")
    # currentBalance = getUserInfo(UID, "currentBalance")

def addUsage(data, UID, addNum):
    UID=str(UID)
    totalUsed = getUserInfo(UID, "totalUsed") + addNum
    setUserInfo = setUserInfo(UID, "totalUsed", totalUsed)
    updateCurrentBalance(UID)

def updateCurrentBalance(UID):
    UID=str(UID)
    totalUsed = getUserInfo(UID, "totalUsed")
    totalDeposite = getUserInfo(UID, "totalDeposite")
    currentBalance = totalDeposite - totalUsed
    setUserInfo = setUserInfo(UID, "currentBalance", currentBalance)

def isAuthored(data, UID):
    UID=str(UID)
    # to be done

# 返回根据 UID 查找的指定字段值
def getUserInfo(UID, field):
    # 遍历 users 数组
    for user in userData["users"]:
        if user["UID"] == UID:
            return user.get(field, None)  # 使用 get() 来避免 KeyError 错误
    return None

# 自定义异常类
class UserNotFoundException(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)

class FieldNotFoundException(Exception):
    def __init__(self, message="Field not found"):
        self.message = message
        super().__init__(self.message)

def hashPassword(password, creating_date, creating_time):
    """
    使用创建日期和时间作为盐
    参数:
        password (str): 用户的明文密码。
        creating_date (str): 创建日期，格式如 "20241217"
        creating_time (str): 创建时间，格式如 "120821"
    """
    salt = creating_date + creating_time
    password_with_salt = password + salt
    # sha256
    hashed_password = hashlib.sha256(password_with_salt.encode('utf-8')).hexdigest()
    return hashed_password


# 根据 UID 更新指定字段
def setUserInfo(uid, field, newValue):
    for user in userData["users"]:
        if user["UID"] == uid:
            if field == "userPassword":
                date=user["creatingDate"]
                time=user["creatingTime"]
                newValue = hashPassword(newValue, date, time)
            if field in user:
                user[field] = newValue  # 更新字段
                return user  # 返回更新后的用户信息
            else:
                raise FieldNotFoundException(f"字段 {field} 不存在！")  # 字段不存在时抛出异常
    raise UserNotFoundException(f"Cannot find the information of UID: {uid}")  # 用户未找到时抛出异常




######################################################
# test:
# 测试：'12900001' userName 和 totalUsed
uid_to_update = "12900001"
field_to_update_1 = "userName"  # 更新 userName
new_value_1 = "MuYYY_Updated"  # 新的 userName 值

field_to_update_2 = "totalUsed"  # 更新 totalUsed
new_value_2 = 150  # 新的 totalUsed 值

try:
    # 更新 userName
    updated_user_1 = set_user_info(uid_to_update, field_to_update_1, new_value_1)
    print(f"更新后的用户信息 (userName): {updated_user_1}")

    # 更新 totalUsed
    updated_user_2 = set_user_info(uid_to_update, field_to_update_2, new_value_2)
    print(f"更新后的用户信息 (totalUsed): {updated_user_2}")

except UserNotFoundException as e:
    print(e)  # 打印用户未找到的错误信息
except FieldNotFoundException as e:
    print(e)  # 打印字段未找到的错误信息