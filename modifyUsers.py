import json
from datetime import datetime
import hashlib

with open("userData.json", "r", encoding="utf-8") as file:
    userData = json.load(file)
# userData =
#   {
#       "UID": "12900001",
#       "userName": "MuYYY",
#       "userPhone": "18012341234",
#       "userPassword": "abcdefg",
#       "creatingDate": "20241217",
#       "creatingTime": "120821",
#       "totalDeposit": 100000,
#       "totalUsed": 100,
#       "currentBalance": 99900
#   }
#   data = {
#       "todo": "addUser",
#       "userName": "ABC",
#       "userPhone": "18012341234",
#       "userPassword": "abcdefg"
#       }
#   data = {
#       "todo": "xxxxx",
#       "UID": "12900001",


# interface begin at here
def modifyUserFunc(dataFromWeb):
    todo = dataFromWeb.get("todo")
    # "todo" means the operation that the user wants to do

    if todo == None:
        return -1

    # because addUser do not need UID,
    # so we do not need to check UID here
    elif todo == "addUser":
        addUserFunc(dataFromWeb)
        return 0
    elif todo == "updateUser":
        updateUserFunc(dataFromWeb)
        return 0
    elif todo == "findUser":
        findUserFunc(dataFromWeb)
        return 0
    elif todo == "rechargeAccount":
        # -1: negative balance; other number: balance
        return rechargeAccount(dataFromWeb)
    elif todo == "addUsage":
        # -1: negative balance; other number: balance
        # this would not get from web, but from the server
        # but we will use the same data structure
        return addUsage(dataFromWeb)
    elif todo == "updateCurrentBalance":
        return updateCurrentBalance(dataFromWeb)
    elif todo == "isAuthored":
        return isAuthored(dataFromWeb)
    # if UID is none but userPhone is not none,
    # we can get UID by userPhone
    UID = dataFromWeb.get("UID")
    if UID == None:
        userPhone = dataFromWeb.get("userPhone")
        if userPhone == None or userPhone == "":
            return -1
        else:
            UID = str(getUserInfoByPhone(userPhone))
            if UID == None:
                return -1
            else:
                dataFromWeb["UID"] = UID

    # interface
    elif todo == "updateUser":
        updateUserFunc(dataFromWeb)
        return 0
    elif todo == "findUser":
        findUserFunc(dataFromWeb)
        return 0
    elif todo == "rechargeAccount":
        # -1: negative balance; other number: balance
        return rechargeAccount(dataFromWeb)
    elif todo == "addUsage":
        # -1: negative balance; other number: balance
        # this would not get from web, but from the server
        # but we will use the same data structure
        return addUsage(dataFromWeb)
    elif todo == "updateCurrentBalance":
        updateCurrentBalance(dataFromWeb)
        return 0
    elif todo == "isAuthored":
        isAuthored(dataFromWeb)
        return 0
    else:
        return -1


###
# second level interfaces
def addUserFunc(dataFromWeb):
    print("Now is in addUserFunc")
    createUser(dataFromWeb)


def updateUserFunc(dataFromWeb):
    print("Now is in updateUserFunc")
    UID = dataFromWeb.get("UID")
    field = dataFromWeb.get("field")
    newValue = dataFromWeb.get("newValue")
    try:
        setUserInfo(UID, field, newValue)
    except UserNotFoundException as e:
        print(e)  # Print user not found error message
        return "eroor: no such user"
    except FieldNotFoundException as e:
        print(e)  # Print field not found error message
        return "error: no such field"


def findUserFunc(dataFromWeb):
    print("Now is in findUserFunc")
    UID = dataFromWeb.get("UID")
    field = dataFromWeb.get("field")
    userInfo = getUserInfo(UID, field)
    return userInfo


# end of the interfaces
###########


def createUser(dataFromWeb, deposit = 0):
    # deposit is optional, default is 0
    # if we want to give an initial amount,
    # we can set deposit to a positive number
    if deposit < 0:
        return -1
    print("Now is in addUserFunction")
    userName = dataFromWeb.get("userName")
    userPhone = dataFromWeb.get("userPhone")
    userPassword = dataFromWeb.get("userPassword")
    current_time = datetime.now()
    creating_date = current_time.strftime("%Y%m%d")  # "20241217"
    creating_time = current_time.strftime("%H%M%S")  # "120821"
    userHashedPassword = hashPassword(userPassword, creating_date, creating_time)
    # find the largest UID
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
        "userPassword": userHashedPassword,
        "creatingDate": creating_date,
        "creatingTime": creating_time,
        "totalDeposit": int(deposit),
        "totalUsed": 0,
        "currentBalance": int(deposit),
    }
    userData["users"].append(new_user)
    with open("userData.json", "w", encoding="utf-8") as file:
        json.dump(userData, file, ensure_ascii=False, indent=4)
    
    # Note: Printing passwords is a security risk!!!
    # Avoid doing this in production.
    # print the new user information
    print(f"New user {userName} created successfully, UID is {new_uid}. Password is {userPassword}")
    return new_user


def rechargeAccount(data):
    UID = data.get("UID")
    addNum = data.get("addNum")
    UID = str(UID)
    totalDeposite = getUserInfo(UID, "totalDeposite") + addNum
    setUserInfo(UID, "totalDeposite", totalDeposite)
    currentBalance = updateCurrentBalance(UID)
    if currentBalance <= 0:
        return -1
    return currentBalance


def addUsage(data, addNum):
    UID = data.get("UID")
    totalUsed = data.get("totalUsed") + addNum
    setUserInfo = setUserInfo(UID, "totalUsed", totalUsed)
    remaining = updateCurrentBalance(UID)
    if remaining <= 0:
        return -1
    else:
        return remaining

def updateCurrentBalance(UID):
    UID = str(UID)
    totalUsed = getUserInfo(UID, "totalUsed")
    totalDeposite = getUserInfo(UID, "totalDeposite")
    currentBalance = totalDeposite - totalUsed
    setUserInfo = setUserInfo(UID, "currentBalance", currentBalance)
    return currentBalance


def getUserInfoByPhone(userPhone):
    for user in userData["users"]:
        if user["userPhone"] == userPhone:
            return user["UID"]
    return None


def isAuthored(dataFromWeb):
    UID = getUserInfoByPhone(dataFromWeb.get("userPhone"))
    if UID == None or UID == "":
        UID = dataFromWeb.get("UID")
        if UID == None or UID == "":
            raise Exception("user's UID or Phone is required")
    userPassword = dataFromWeb.get("userPassword")
    if userPassword == None:
        raise Exception("user's Password is required")

    for user in userData["users"]:
        if user["UID"] == UID:
            creatingDate = user.get("creatingDate")
            creatingTime = user.get("creatingTime")
            if creatingDate == None or creatingTime == None:
                raise Exception("creatingDate and creatingTime are required")
            if user["userPassword"] == hashPassword(
                userPassword, creatingDate, creatingTime
            ):
                return True
            else:
                return False


# 返回根据 UID 查找的指定字段值
def getUserInfo(UID, field):
    # 遍历 users 数组
    for user in userData["users"]:
        if user["UID"] == UID:
            return user.get(field, None)
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
    Use the creation date and time as salt.
    Parameters:
        password (str): The user's plaintext password.
        creating_date (str): Creation date, formatted as "20241217".
        creating_time (str): Creation time, formatted as "120821".
    """
    salt = creating_date + creating_time
    password_with_salt = password + salt
    # sha256
    hashed_password = hashlib.sha256(password_with_salt.encode("utf-8")).hexdigest()
    return hashed_password


# 根据 UID 更新指定字段
def setUserInfo(uid, field, newValue):
    for user in userData["users"]:
        if user["UID"] == uid:
            if field == "userPassword":
                date = user["creatingDate"]
                time = user["creatingTime"]
                newValue = hashPassword(newValue, date, time)
            if field in user:
                user[field] = newValue  # update the field
                return user  # return the updated user information
            else:
                raise FieldNotFoundException(
                    f"Field {field} does not exist!"
                )  # Raise an exception if the field does not exist
    raise UserNotFoundException(
        f"Cannot find the information of UID: {uid}"
    )  # Raise an exception if the user is not found


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
    updated_user_1 = setUserInfo(uid_to_update, field_to_update_1, new_value_1)
    print(f"更新后的用户信息 (userName): {updated_user_1}")

    # 更新 totalUsed
    updated_user_2 = setUserInfo(uid_to_update, field_to_update_2, new_value_2)
    print(f"更新后的用户信息 (totalUsed): {updated_user_2}")

except UserNotFoundException as e:
    print(e)  # 打印用户未找到的错误信息
except FieldNotFoundException as e:
    print(e)  # 打印字段未找到的错误信息
