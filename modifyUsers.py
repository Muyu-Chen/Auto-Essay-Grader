import json
from datetime import datetime
import hashlib

with open("userData.json", "r", encoding="utf-8") as file:
    userData = json.load(file)
# userData =
#   {
#       "UID": "12900001",
#       "userName": "MuYYY",
#       "userAccount": "18012341234",
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
#       "userAccount": "18012341234",
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
        return addUserFunc(dataFromWeb)
    elif todo == "updateUser":
        updateUserFunc(dataFromWeb)
        return 0
    elif todo == "findUserField":
        return findUserFunc(dataFromWeb)
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
    elif todo == "isVerified":
        return isVerified(dataFromWeb)
    elif todo == "generateUserTempToken":
        return generateUserTempToken(dataFromWeb)
    # if UID is none but userAccount is not none,
    # we can get UID by userAccount
    UID = dataFromWeb.get("UID")
    if UID == None:
        userAccount = dataFromWeb.get("userAccount")
        if userAccount == None or userAccount == "":
            return -1
        else:
            UID = str(getUserInfoByAccount(userAccount))
            if UID == None:
                return -1
            else:
                dataFromWeb["UID"] = UID

    # interface
    elif todo == "updateUser":
        updateUserFunc(dataFromWeb)
        return 0
    elif todo == "findUser":
        return findUserFunc(dataFromWeb)
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
    elif todo == "isVerified":
        isVerified(dataFromWeb)
        return 0
    else:
        return -1


###
# second level interfaces
def addUserFunc(dataFromWeb):
    print("Now is in addUserFunc")
    return createUser(dataFromWeb)


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
    if UID == None:
        userAccount = dataFromWeb.get("userAccount")
        if userAccount == None or userAccount == "":
            return None
        else:
            UID = str(getUserInfoByAccount(userAccount))
            # if UID is None, means the user is not found
    field = dataFromWeb.get("field")
    print(f"UID: {UID}, field: {field}")
    userInfo = getUserInfo(UID, field)
    print(f"userInfo: {userInfo}")
    return userInfo


# end of the interfaces
###########


def createUser(dataFromWeb, deposit=0):
    # deposit is optional, default is 0
    # if we want to give an initial amount,
    # we can set deposit to a positive number
    if deposit < 0:
        return -1
    print("Now is in addUserFunction")
    userName = dataFromWeb.get("userName")
    userAccount = dataFromWeb.get("userAccount")
    userPassword = dataFromWeb.get("userPassword")
    current_time = datetime.now()
    creating_date = current_time.strftime("%Y%m%d")  # "20241217"
    creating_time = current_time.strftime("%H%M%S")  # "120821"
    userHashedPassword = hashPassword(userPassword, creating_date, creating_time)
    # find the largest UID
    max_uid = 0
    with open("userData.json", "r", encoding="utf-8") as file:
        userDataNow = json.load(file)
    for user in userDataNow["users"]:
        try:
            max_uid = max(max_uid, int(user["UID"]))
        except ValueError:
            continue
    new_uid = str(max_uid + 1)
    new_user = {
        "UID": new_uid,
        "userName": userName,
        "userAccount": userAccount,
        "userPassword": userHashedPassword,
        "creatingDate": creating_date,
        "creatingTime": creating_time,
        "totalDeposit": int(deposit),
        "totalUsed": 0,
        "currentBalance": int(deposit),
    }
    userDataNow["users"].append(new_user)
    with open("userData.json", "w", encoding="utf-8") as file:
        json.dump(userDataNow, file, ensure_ascii=False, indent=4)

    # Note: Printing passwords is a security risk!!!
    # Avoid doing this in production.
    # print the new user information
    print(
        f"New user {userName} created successfully, UID is {new_uid}. Password is {userPassword}"
    )
    return new_user


def rechargeAccount(data):
    UID = str(data.get("UID"))
    if UID == None or UID == "":
        UID = str(getUserInfoByAccount(data.get("userAccount")))
    addNum = data.get("addNum")
    print(f"UID: {UID}, addNum: {addNum}")
    if str(addNum) == "type1" or str(addNum) == "type2":
        # some function to change the addNum to a number
        pass
    else:
        addNum = int(addNum)
    print(str(getUserInfo(UID, "totalDeposit")))
    totalDeposit = int(getUserInfo(UID, "totalDeposit")) + addNum
    print(f"totalDeposit: {totalDeposit}")
    setUserInfo(UID, "totalDeposit", int(totalDeposit))
    print("the first time to call setUserInfo")
    currentBalance = updateCurrentBalance(UID)
    if currentBalance <= 0:
        return -1
    return currentBalance


def addUsage(data):
    UID = data.get("UID")
    if UID == None or UID == "":
        UID = str(getUserInfoByAccount(data.get("userAccount")))
    addNum = data.get("addNum")
    totalUsed = getUserInfo(UID, "totalUsed")
    print("totalUsed: " + str(totalUsed))
    if UID == None or UID == "":
        UID = str(getUserInfoByAccount(data.get("userAccount")))
    if isVerified(data) == False:
        return -1
    totalUsedNew = totalUsed + addNum
    temp1 = setUserInfo(UID, "totalUsed", totalUsedNew)
    remaining = updateCurrentBalance(UID)
    if remaining <= 0:
        return -1
    else:
        return remaining

def updateCurrentBalance(UID):
    UID = str(UID)
    totalUsed = getUserInfo(UID, "totalUsed")
    totalDeposit = getUserInfo(UID, "totalDeposit")
    currentBalance = totalDeposit - totalUsed
    setUserInfo(UID, "currentBalance", currentBalance)
    return currentBalance


def getUserInfoByAccount(userAccount):
    with open("userData.json", "r", encoding="utf-8") as file:
        userDataNow = json.load(file)
    for user in userDataNow["users"]:
        if str(user["userAccount"]) == str(userAccount):
            return user["UID"]
    return None


def isVerified(dataFromWeb):
    print("now is in “isVerified”, phone: " + str(dataFromWeb.get("userAccount")))
    print("uerPassword: " + str(dataFromWeb.get("userPassword")))
    UID = getUserInfoByAccount(str(dataFromWeb.get("userAccount")))
    print(f"UID: {UID}")
    if UID == None or UID == "":
        UID = dataFromWeb.get("UID")
        if UID == None or UID == "":
            raise Exception("no such user!")
    userPassword = dataFromWeb.get("userPassword")
    if userPassword == None:
        raise Exception("user's Password is required")
    with open("userData.json", "r", encoding="utf-8") as file:
        userDataNow = json.load(file)
    for user in userDataNow["users"]:
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
    with open("userData.json", "r", encoding="utf-8") as file:
        userDataNow = json.load(file)
    if field is None or field == "":
        return None
    # 遍历 users 数组
    for user in userDataNow["users"]:
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
    with open("userData.json", "r", encoding="utf-8") as file:
        userDataNow = json.load(file)
    for user in userDataNow["users"]:
        if user["UID"] == uid:
            if field == "userPassword":
                date = user["creatingDate"]
                time = user["creatingTime"]
                newValue = hashPassword(newValue, date, time)
            if field in user:
                user[field] = newValue  # update the field
                print(f"Field {field} updated successfully!" f" New value: {newValue}")
                with open("userData.json", "w") as f:
                    print("write to file")
                    json.dump(userDataNow, f, ensure_ascii=False, indent=4)
                    print("write to file done")
                return user  # return the updated user information
            else:
                raise FieldNotFoundException(
                    f"Field {field} does not exist!"
                )  # Raise an exception if the field does not exist
    raise UserNotFoundException(
        f"Cannot find the information of UID: {uid}"
    )  # Raise an exception if the user is not found


def generateUserTempToken(dataFromWeb):
    userAccount = dataFromWeb.get("userAccount")
    experitedTime = dataFromWeb.get("experitedTime")  # hours
    if experitedTime == None or experitedTime == "":
        experitedTime = 14 * 24  # 14 days
    if userAccount == None or userAccount == "":
        UID = dataFromWeb.get("UID")
        if UID == None:
            return -1
    userAccount = getUserInfo(UID, "userAccount")
    createTime = datetime.now().strftime("%Y%m%d%H%M%S")
    return hashPassword(userAccount, createTime, experitedTime)


######################################################
# test:
# 测试：'12900001' userName 和 totalUsed
# uid_to_update = "12900001"
# field_to_update_1 = "userName"  # 更新 userName
# new_value_1 = "MuYYY_Updated"  # 新的 userName 值

# field_to_update_2 = "totalUsed"  # 更新 totalUsed
# new_value_2 = 150  # 新的 totalUsed 值

# try:
# 更新 userName
# updated_user_1 = setUserInfo(uid_to_update, field_to_update_1, new_value_1)
# print(f"更新后的用户信息 (userName): {updated_user_1}")

# 更新 totalUsed
# updated_user_2 = setUserInfo(uid_to_update, field_to_update_2, new_value_2)
# print(f"更新后的用户信息 (totalUsed): {updated_user_2}")

# except UserNotFoundException as e:
#    print(e)  # 打印用户未找到的错误信息
# except FieldNotFoundException as e:
#    print(e)  # 打印字段未找到的错误信息
