const API_BASE = window.AEG_API_BASE || "http://127.0.0.1:5000";
const getDataURL = `${API_BASE}/getData`;
const loginPage = "../index.html";
const chargePage = "../../charge/index.html";
let timeDeley = 0;

// data
let curUserName = "未命名用户";
let curEmail = "email@eamil.com";
let curPersonalBio = "(可修改)保持好奇，探索未知";
let curPhoneNumber = "123 1234 1234";

let newUserName = "";
let newEmail = "";
let newPersonalBio = "";
let newPhoneNumber = "";


function startFunc() {
    let curBalance = localStorage.getItem("balance");
    let curUID = localStorage.getItem("UID");
    if (curBalance == undefined) {
        if (curUID == undefined) {
            curBalance = 0;
            curUID = "00000000";
        }
    }
    document.getElementById("UID").innerText = curUID;
    document.getElementById("balance").innerText = curBalance;

    getUserData();
}

function getUserData() {
    const balance = document.getElementById("balance").value;
    console.log("here in getBalance");
    const userAccount = localStorage.getItem("userAccount");
    const userPassword = localStorage.getItem("userPassword");
    console.log(userAccount);
    if (userAccount === null || userPassword === null) {
        console.error("无账号密码，请重新登录");
        alert("无法识别账号密码，请重新登录");
        window.location.href = loginPage;
    }
    fetch(getDataURL + `?userAccount=${encodeURIComponent(userAccount)}&userPassword=${encodeURIComponent(userPassword)}&todo=getData`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then((response) => {
            if (response.status === 200) {
                return response.json();
            } else if (response.status === 400) {
                console.log("getUser Data's status is 400");
                let returnValue = response.json();
                throw new Error(returnValue.error);
            }
        })
        .then((data) => {
            let curBalance = data.currentBalance;
            let curUID = data.UID;
            if (curBalance !== undefined) {
                if (curUID !== undefined) {
                    timeDeley = 0;
                    console.log("UID: ", curUID);
                    console.log("Balance: ", curBalance);

                    if (!(data.userName == undefined || data.userName == "")) {
                        curUserName = data.userName;
                        newUserName = curUserName;
                    }
                    else {
                        newUserName = curUserName;
                    }
                    if (!(data.email == undefined || data.email == "")) {
                        curEmail = data.email;
                        newEmail = curEmail;
                    }
                    else {
                        newEmail = curEmail;
                    }
                    if (!(data.personalBio == undefined || data.personalBio == "")) {
                        curPersonalBio = data.personalBio;
                        newPersonalBio = curPersonalBio;
                    }
                    else {
                        newPersonalBio = curPersonalBio;
                    }
                    console.log("phoneNumber: ", data.phoneNumber);
                    if (!(data.phoneNumber == undefined || data.phoneNumber == "")) {
                        console.log("phoneNumber: ", data.phoneNumber);
                        curPhoneNumber = data.phoneNumber;
                        newPhoneNumber = curPhoneNumber;
                    }
                    else {
                        console.log("?????");
                        newPhoneNumber = curPhoneNumber;
                    }

                    console.log("userName: ", curUserName);
                    console.log("email: ", curEmail);
                    console.log("personalBio: ", curPersonalBio);
                    console.log("phoneNumber: ", curPhoneNumber);

                    document.querySelector('[data-id="field-UserName"]').innerText = curUserName;
                    document.querySelector('[data-id="field1"]').innerText = curPersonalBio;
                    document.querySelector('[data-id="field2"]').innerText = curEmail;
                    document.querySelector('[data-id="field3"]').innerText = curPhoneNumber;
                    document.getElementById("UID").innerText = curUID;
                    document.getElementById("balance").innerText = curBalance;

                    localStorage.setItem("balance", curBalance);
                    localStorage.setItem("UID", curUID);
                    //这里需要修改 todo
                    const inviteUrl = new URL("../index.html", window.location.href);
                    inviteUrl.searchParams.set("ref", curUID);
                    document.getElementById("refLink").innerText = inviteUrl.toString();
                }
            }
        })
        .catch((error) => {
            console.error("网络错误: ", error);
            document.getElementById("balance").innerText = "Network error, loading...";
            // 休眠5n秒
            timeDeley += 4500; // 增加休眠时间
            console.log("time deley: ", timeDeley);
            setTimeout(() => { getUserData(); }, timeDeley);
        });
}


function charge() {
    window.location.href = chargePage; // 将 "register.html" 替换为你的注册页面链接
}

function boundOtherAccount() {
    alert("功能暂未开放")
}
function changePassword() {
    alert("功能暂未开放")
}

function logout() {
    localStorage.removeItem("userAccount"); // 清空 userAccount
    localStorage.removeItem("userPassword"); // 清空 userPassword
    localStorage.removeItem("userPhone");
    localStorage.removeItem("UID");
    window.location.href = loginPage; // 将 "register.html" 替换为你的注册页面链接
}

function deleteAccount() {
    alert("功能暂未开放")
}


function copyToClipboard() {
    const refLinkElement = document.getElementById("refLink");
    if (!refLinkElement) {
        alert("邀请链接未找到！");
        return;
    }

    const refLink = refLinkElement.innerText || "链接未找到";
    const UID = localStorage.getItem("UID") || "无";
    const temp = `使用注册链接立即开始使用，现在注册立刻免费获得5元额度： ${refLink} 。或在APP中注册，填写邀请码：${UID}`;

    if (navigator.clipboard && window.isSecureContext) {
        // 使用 Clipboard API 进行复制
        navigator.clipboard.writeText(temp).then(() => {
            console.log("refLink: ", temp);
            alert("邀请链接已复制到剪贴板！");
        }).catch(err => {
            console.error("复制失败: ", err);
        });
    } else {
        // 非安全域下使用 textarea 模拟复制
        const textArea = document.createElement("textarea");
        textArea.value = temp;
        textArea.style.position = "absolute";
        textArea.style.left = "-9999px"; // 确保 textarea 不会在页面中可见
        document.body.appendChild(textArea);
        textArea.select();

        try {
            if (document.execCommand("copy")) {
                console.log("refLink: ", temp);
                alert("邀请链接已复制到剪贴板！");
            } else {
                alert("复制失败，请手动复制！");
            }
        } catch (err) {
            console.error("使用 execCommand 复制失败: ", err);
            alert("复制失败，请手动复制！");
        } finally {
            document.body.removeChild(textArea); // 移除临时的 textarea
        }
    }
}

const editableFields = document.querySelectorAll(".editable");
// 绑定点击和失去焦点事件到每个可编辑字段
editableFields.forEach(field => {
    // 点击进入编辑状态
    field.addEventListener("click", () => {
        field.setAttribute("contenteditable", "true"); // 启用编辑模式
        field.classList.add("editing"); // 添加编辑状态样式
        field.focus(); // 聚焦到元素中
    });

    // 失去焦点退出编辑状态
    field.addEventListener("blur", () => {
        field.setAttribute("contenteditable", "false"); // 禁用编辑模式
        field.classList.remove("editing"); // 移除编辑状态样式
        const content = field.innerText.trim(); // 获取编辑后的内容
        const fieldId = field.getAttribute("data-id"); // 获取唯一标识符
        if (content === null || content === "" || content === undefined) {
            console.log("请勿保存空内容")
            const targetElement = document.querySelector(`[data-id="${fieldId}"]`);
            if (targetElement) {
                targetElement.innerText = "请输入内容";
            }
        }
        else {
            saveContent(fieldId, content); // 调用保存函数
        }
    });

    // 按下 Enter 键时退出编辑状态
    field.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault(); // 防止换行
            field.blur(); // 模拟失去焦点
        }
    });
});

// 保存内容的函数
// cur是从服务器获取的数据，不会改变（修改服务器的后会改变）
// new是用户编辑后的新数据
function saveContent(id, content) {
    if (id == "field-UserName") {
        newUserName = content;
    }
    if (id == "field1") {
        newPersonalBio = content;
    }
    if (id == "field2") {
        const emailRegex = new RegExp(
            "^(?:(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*)|(?:\"(?:\\\\[\\x01-\\x7f]|[^\\x01-\\x7f\\\\\"])*\"))" +
            "@(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\\.)+[a-zA-Z]{2,}|(?:\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}" +
            "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\]))$"
        );
        if (!emailRegex.test(content)) {
            console.error("未保存：无效的邮箱地址");
            alert("未保存：请输入有效的邮箱地址");
            return;
        }
        newEmail = content;
    }
    if (id == "field3") {
        const phoneRegex = /^(?:\+86\s?)?(?:\d{3}\s?\d{4}\s?\d{4}|\d{11})$/;
        if (!phoneRegex.test(content)) {
            console.error("未保存：无效的电话号码");
            alert("未保存：请输入有效的电话号码");
            return;
        }
        newPhoneNumber = content;
    }
    if (id == "field4") {
        // 语言设置
    }
    console.log(`保存字段 ${id} 的内容:`, content);
    // field-UserName: userName
    // field1: 个性签名；field2: 邮箱；field3: 电话号码；field4: 语言设置
    // 此处可添加保存逻辑，例如通过 fetch 提交到服务器
    if (newUserName != curUserName) {
        saveUserData("userName", newUserName);
        curUserName = newUserName;
    }
    if (newPersonalBio != curPersonalBio) {
        saveUserData("personalBio", newPersonalBio);
        curPersonalBio = newPersonalBio;
    }
    if (newEmail != curEmail) {
        saveUserData("email", newEmail);
        curEmail = newEmail;
    }
    if (newPhoneNumber != curPhoneNumber) {
        console.log("newPhoneNumber: ", newPhoneNumber);
        console.log("curPhoneNumber: ", curPhoneNumber);
        saveUserData("phoneNumber", newPhoneNumber);
        curPhoneNumber = newPhoneNumber;
    }

}

function saveUserData(field, value) {
    console.log("here in saveUserData");
    console.log("field: ", field);
    console.log("value: ", value);
    const userAccount = localStorage.getItem("userAccount");
    const userPassword = localStorage.getItem("userPassword");
    fetch(getDataURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userAccount": userAccount,
            "userPassword": userPassword,
            "todo": "setData",
            "field": field,
            "newValue": value,
        }),
    })
        .then((response) => {
            if (response.status === 200) {
                console.log("保存成功");
            } else {
                console.error("保存失败，失败代码: ", response.status);
                console.error(response.json());
            }
        })
        .catch((error) => {
            console.error("保存失败，网络错误:", error);
        });
}





window.addEventListener("load", startFunc);
