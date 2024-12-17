import json
from datetime import datetime

with open('userData.json', 'r', encoding='utf-8') as file:
    userData = json.load(file)

def createUser(data):
    print("Now is in addUserFunction")
    userName=data.get("userName")
    userPassword=data.get("userPassword")
    current_time = datetime.now()
    creating_date = current_time.strftime("%Y%m%d")  # "20241217"
    creating_time = current_time.strftime("%H%M%S")  # "120821"

def rechargeAccount(data, UID, addNum):
    UID = (string)(UID)
    totalDeposite = getUserInfo(UID, "totalDeposite") + addNum
    setUserInfo(UID, "totalDeposite", totalDeposite)
    # totalUsed = getUserInfo(UID, "totalUsed")
    # currentBalance = getUserInfo(UID, "currentBalance")

def addUsage(data, UID, addNum):
    UID = (string)(UID)
    totalUsed = getUserInfo(UID, "totalUsed") + addNum
    setUserInfo = setUserInfo(UID, "totalUsed", totalUsed)
    updateCurrentBalance(data, UID)

def updateCurrentBalance(data, UID):
    UID = (string)(UID)
    totalUsed = getUserInfo(UID, "totalUsed")
    totalDeposite = getUserInfo(UID, "totalDeposite")
    currentBalance = totalDeposite - totalUsed
    setUserInfo = setUserInfo(UID, "currentBalance", currentBalance)


# 返回根据 UID 查找的指定字段值
def getUserInfo(UID, field):
    # 遍历 users 数组
    for user in json_data["users"]:
        if user["UID"] == UID:
            return user.get(field, None)  # 使用 get() 来避免 KeyError 错误
    return None  # 如果没有找到 UID，返回 None

# 自定义异常类
class UserNotFoundException(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)

class FieldNotFoundException(Exception):
    def __init__(self, message="Field not found"):
        self.message = message
        super().__init__(self.message)

# 根据 UID 更新指定字段
def setUserInfo(uid, field, new_value):
    for user in json_data["users"]:
        if user["UID"] == uid:
            if field in user:
                user[field] = new_value  # 更新字段
                return user  # 返回更新后的用户信息
            else:
                raise FieldNotFoundException(f"字段 {field} 不存在！")  # 字段不存在时抛出异常
    raise UserNotFoundException(f"未找到 UID {uid} 的用户信息。")  # 用户未找到时抛出异常




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