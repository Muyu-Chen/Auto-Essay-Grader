import json
from datetime import datetime
import hashlib
from os import path
import threading

DEBUG_MODEL = False

BASE_DIR = path.dirname(path.abspath(__file__))
userDataFile = path.join(BASE_DIR, "..", "src", "userData.json")
with open(userDataFile, "r", encoding="utf-8") as file:
    userData = json.load(file)

DEFAULT_USER_FIELDS = {
    "phoneNumber": "",
    "email": "",
    "personalBio": "",
    "priceLevel": 100,
    "referredByUID": "0",
    "version": "",
    "lastLoginTime": "",
    "isProcessing": "false",
}
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
    filed = dataFromWeb.get("field")
    if DEBUG_MODEL:
        print("Now is in modifyUserFunc")
        print("todo: " + str(todo) + "; field: " + str(filed))
    # "todo" means the operation that the user wants to do

    if todo == None:
        raise Exception("没有操作“todo”，请检查输入")

    # because addUser do not need UID,
    # so we do not need to check UID here
    if todo == "addUser":
        return addUserFunc(dataFromWeb)

    # if UID is none but userAccount is not none,
    # we can get UID by userAccount
    UID = dataFromWeb.get("UID")
    if UID == None or UID == "" or UID == "None":
        userAccount = dataFromWeb.get("userAccount")
        if DEBUG_MODEL:
            print("userAccount: " + str(userAccount))
        if userAccount == None or userAccount == "":
            raise Exception("没有输入userAccount，请检查输入")
        else:
            UID = str(getUserInfoByAccount(userAccount))
            if UID == None or UID == "" or UID == "None":
                raise Exception("no such user")
            else:
                print("UID: " + str(UID))
                dataFromWeb["UID"] = UID

    # interface

    if todo == "updateUser":
        # dataFromWeb:
        # UID = dataFromWeb.get("UID")
        # field = dataFromWeb.get("field")
        # newValue = dataFromWeb.get("newValue")
        return updateUserFunc(dataFromWeb)

    elif todo == "rechargeAccount":
        # -1: negative balance; other number: balance
        return rechargeAccount(dataFromWeb)
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
        print("Now is before isVerified")
        return isVerified(dataFromWeb)
    elif todo == "generateUserTempToken":
        return generateUserTempToken(dataFromWeb)
    else:
        print("No such operation" + str(todo))
        raise Exception("没有对应操作：" + str(todo))


###
# second level interfaces
def addUserFunc(dataFromWeb):
    print("Now is in addUserFunc")
    return createUser(dataFromWeb, 5) # 5 is the initial deposit


def updateUserFunc(dataFromWeb):
    print("Now is in updateUserFunc")
    UID = dataFromWeb.get("UID")
    field = dataFromWeb.get("field")
    newValue = dataFromWeb.get("newValue")
    try:
        setUserInfo(UID, field, newValue)
    except UserNotFoundException as e:
        print(e)  # Print user not found error message
        # "eroor: no such user"
        return 401
    except FieldNotFoundException as e:
        print(e)  # Print field not found error message
        # "error: no such field"
        return 402
    return 200


def findUserFunc(dataFromWeb):
    if DEBUG_MODEL:
        print("Now is in findUserFunc")
    UID = dataFromWeb.get("UID")
    if UID == None or UID == "" or UID == "None":
        userAccount = dataFromWeb.get("userAccount")
        if userAccount == None or userAccount == "":
            raise Exception("没有输入userAccount，请检查输入")
        else:
            UID = str(getUserInfoByAccount(userAccount))
            # if UID is None, means the user is not found
    field = dataFromWeb.get("field")
    if field == None or field == "" or field == "None":
        raise Exception("没有输入field，请检查输入")
    if DEBUG_MODEL:
        print(f"UID: {UID}, field: {field}")
    userInfo = getUserInfo(UID, field)
    if DEBUG_MODEL:
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
    if userName == None or userName == "" or userName == "None":
        userName = userAccount
    userPassword = dataFromWeb.get("userPassword")
    referredByUID = dataFromWeb.get("referredByUID")
    # todo: 通过邀请链接来获得priceLevel
    priceLevel = 100
    current_time = datetime.now()
    creating_date = current_time.strftime("%Y%m%d")  # "20241217"
    creating_time = current_time.strftime("%H%M%S")  # "120821"
    userHashedPassword = hashPassword(userPassword, creating_date, creating_time)
    # find the largest UID
    max_uid = 0
    with open(userDataFile, "r", encoding="utf-8") as file:
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
        "phoneNumber": "",
        "email": "",
        "personalBio": "",
        "userPassword": userHashedPassword,
        "creatingDate": creating_date,
        "creatingTime": creating_time,
        "priceLevel": priceLevel,
        "referredByUID": str(referredByUID),
        "version": "",
        "lastLoginTime": "",
        "totalDeposit": int(deposit),
        "totalUsed": 0,
        "currentBalance": int(deposit),
    }
    userDataNow["users"].append(new_user)
    # write the new user: 写入
    with open(userDataFile, "w", encoding="utf-8") as file:
        json.dump(userDataNow, file, ensure_ascii=False, indent=4)

    # Note: Printing passwords is a security risk!!!
    # Avoid doing this in production.
    # print the new user information
    print(
        f"New user {userName} created successfully, UID is {new_uid}. Password is {userPassword}"
    )
    return new_user


def ensure_user_defaults(uid):
    with open(userDataFile, "r", encoding="utf-8") as file:
        user_data_now = json.load(file)

    has_changes = False
    for user in user_data_now["users"]:
        if user["UID"] != uid:
            continue
        for field, default_value in DEFAULT_USER_FIELDS.items():
            if field not in user:
                user[field] = default_value
                has_changes = True
        break

    if has_changes:
        with open(userDataFile, "w", encoding="utf-8") as file:
            json.dump(user_data_now, file, ensure_ascii=False, indent=4)


def rechargeAccount(data):
    UID = str(data.get("UID"))
    if UID == None or UID == "" or UID == "None":
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
    if UID == None or UID == "" or UID == "None":
        UID = str(getUserInfoByAccount(data.get("userAccount")))
    addNum = data.get("addNum")
    totalUsed = getUserInfo(UID, "totalUsed")
    print("totalUsed: " + str(totalUsed))
    if UID == None or UID == "" or UID == "None":
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
    with open(userDataFile, "r", encoding="utf-8") as file:
        userDataNow = json.load(file)
    for user in userDataNow["users"]:
        if str(user["userAccount"]) == str(userAccount):
            return user["UID"]
    return None


def isVerified(dataFromWeb):
    print(dataFromWeb)
    if DEBUG_MODEL:
        print("now is in “isVerified”, Account: " + str(dataFromWeb.get("userAccount")))
        print("uerPassword: " + str(dataFromWeb.get("userPassword")))
    UID = getUserInfoByAccount(str(dataFromWeb.get("userAccount")))
    print(f"UID: {UID}")
    if UID == None or UID == "" or UID == "None":
        UID = dataFromWeb.get("UID")
        if UID == None or UID == "" or UID == "None":
            print("no such user")
            raise Exception("no such user")
    ensure_user_defaults(UID)
    userPassword = dataFromWeb.get("userPassword")

    # 更新用户正在使用的版本号和最新登录时间
    isLogin = dataFromWeb.get("isLogin")

    if isLogin == "False" or isLogin == False or isLogin == "false":
        if DEBUG_MODEL:
            print("is in isVerified, but isLogin is False")
        # 不更新版本号
    elif isLogin == "True" or isLogin == True or isLogin == "true":
        userVersion = dataFromWeb.get("version")
        if userVersion == None or userVersion == "" or userVersion == "None":
            if DEBUG_MODEL:
                print("user is using app version, but there is no version number")
            # 不更新版本号
            pass
        elif userVersion == "web":
            if DEBUG_MODEL:
                print("user is using web version")
        else:
            setUserInfo(UID, "version", userVersion)
        # 更新最新登录时间
        lastLoginTime = datetime.now().strftime("%Y%m%d%H%M")
        setUserInfo(UID, "lastLoginTime", lastLoginTime)
    else:
        if DEBUG_MODEL:
            print("在isVerified中，没有更新版本号，因为isLogin不是True也不是False")
            print("isLogin: " + str(isLogin))
        else:
            print("错误：在modifyUsers.py - isVerified (1)")

    if userPassword == None or userPassword == "" or userPassword == "None":
        raise Exception("no password")
    with open(userDataFile, "r", encoding="utf-8") as file:
        userDataNow = json.load(file)
    for user in userDataNow["users"]:
        if user["UID"] == UID:
            creatingDate = user.get("creatingDate")
            creatingTime = user.get("creatingTime")
            if creatingDate == None or creatingTime == None or creatingDate == "" or creatingTime == "" or creatingDate == "None" or creatingTime == "None":
                raise Exception("no creating time")
            if user["userPassword"] == hashPassword(
                userPassword, creatingDate, creatingTime
            ):
                return True
            else:
                return False


# 返回根据 UID 查找的指定字段值
def getUserInfo(UID, field):
    with open(userDataFile, "r", encoding="utf-8") as file:
        userDataNow = json.load(file)
    if field is None or field == "" or field == "None":
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
    with open(userDataFile, "r", encoding="utf-8") as file:
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
                # update new field: 写入
                file_lock = threading.Lock()
                with file_lock:
                    with open(userDataFile, "w", encoding="utf-8") as f:
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
    if experitedTime == None or experitedTime == "" or experitedTime == "None":
        experitedTime = 14 * 24  # 14 days
    if userAccount == None or userAccount == "" or userAccount == "None":
        UID = dataFromWeb.get("UID")
        if UID == None or UID == "" or UID == "None":
            return -1
    userAccount = getUserInfo(UID, "userAccount")
    createTime = datetime.now().strftime("%Y%m%d%H%M%S")
    return hashPassword(userAccount, createTime, experitedTime)
