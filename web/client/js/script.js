const API_BASE = window.AEG_API_BASE || "http://127.0.0.1:5000";
const loginURL = `${API_BASE}/login`;
const chargeURL = `${API_BASE}/charge`;
const registerURL = `${API_BASE}/register`;
const getDataURL = `${API_BASE}/getData`;
const processFileURL = `${API_BASE}/process`;
const checkStatusURL = `${API_BASE}/checkStatus`;
const mainPage = "./mainpage.html";
const loginPage = "./index.html";
const chargePage = "../charge/index.html";

let timeDeley = 0;

function login() {
    const userAccount = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    console.log(userAccount);
    console.log(password);
    if (userAccount === "" || password === "") {
        document.getElementById("login-error").innerText = "账号密码不能为空";
        return;
    }
    fetch(loginURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userAccount": userAccount,
            "userPassword": password,
            "todo": "isVerified",
            "version": "web",
            "isLogin": "true"
        }),
    })
        .then((response) => {
            console.log(response.status);
            if (response.status === 200) {
                console.log("status is 200");
                return response.json(); // 返回一个 Promise
            } else if (response.status === 401) {
                throw new Error('password-error');
            }
            else if (response.status === 504) {
                return response.json();
            }
        })
        .then((data) => {
            console.log(data);
            if (data.message) {
                localStorage.setItem("userAccount", userAccount); // 保存 userID 到 localStorage
                localStorage.setItem("userPassword", password); // 保存 userID 到 localStorage
                window.location.href = mainPage; // 将 "register.html" 替换为你的注册页面链接
            }
            else if (data.error) {
                if (data.error === "no such user") {
                    document.getElementById("login-error").innerText = "用户不存在，请检查账号或注册。";
                }
                else if (data.error === "no password") {
                    document.getElementById("login-error").innerText = "用户注册时未设置密码，请联系管理员。";
                }
                else if (data.error === "no creating time") {
                    document.getElementById("login-error").innerText = "用户注册时未设置创建时间，请联系管理员。";
                }
                else {
                    console.log(data.error);
                    throw new Error('登录失败 ' + data.error);
                }
            }
            else {
                throw new Error('登录失败');
            }
        })
        .catch((error) => {
            if (error.message === 'password-error') {
                document.getElementById("login-error").innerText = "登录失败，请检查账号密码";
            }
            else if (error.message.includes('登录失败')) {
                document.getElementById("login-error").innerText = "未知错误，请联系管理员: " + error.message;
            }
            else {
                document.getElementById("login-error").innerText = "服务器错误，请稍后重试";
            }
        });
}

function getBalance() {
    console.log("here in getBalance");
    const userAccount = localStorage.getItem("userAccount");
    const userPassword = localStorage.getItem("userPassword");
    console.log(userAccount);
    if (userAccount === null || userPassword === null) {
        console.error("无账号密码，请重新登录");
        alert("无法识别账号密码，请重新登录");
        window.location.href = loginPage;
    }

    fetch(getDataURL + `?userAccount=${encodeURIComponent(userAccount)}&userPassword=${encodeURIComponent(userPassword)}&todo=getBalance`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.currentBalance !== undefined) {
                document.getElementById("balance").innerText = data.currentBalance;
                localStorage.setItem("balance", data.currentBalance);
            }
        })
        .catch((error) => {
            console.error("网络错误:", error);
            document.getElementById("balance").innerText = "Network error, loading...";
            // 休眠2n秒
            timeDeley += 2000; // 增加休眠时间
            console.log("time deley: ", timeDeley);
            setTimeout(() => { getBalance(); }, timeDeley);
        });
}

function charge() {
    const cardCode = document.getElementById("card-code").value;
    const userAccount = localStorage.getItem("userAccount");
    const userPassword = localStorage.getItem("userPassword");
    fetch(chargeURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userAccount": userAccount,
            "userPassword": userPassword,
            "todo": "charge",
            "cardPIN": cardCode
        }),
    })
        .then((response) => {
            if (response.status === 200) {
                document.getElementById("recharge-message").innerText = "充值成功";
                //弹窗
                alert("充值成功！");
                getBalance();
            } else {
                document.getElementById("recharge-message").innerText = "充值失败";
            }
        })
        .catch(() => {
            document.getElementById("recharge-message").innerText = "服务器错误，请稍后重试";
        });
}

// 注册页面逻辑
function showRegisterPage() {
    document.getElementById('login-page-display-control').style.display = 'none';
    document.getElementById('register-page-display-control').style.display = 'block';
}

function showLoginPage() {
    document.getElementById('register-page-display-control').style.display = 'none';
    document.getElementById('login-page-display-control').style.display = 'block';
}

async function register() {
    const userAccount = document.getElementById('register-username').value;
    const userPassword = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;

    if (userPassword !== confirmPassword) {
        document.getElementById('register-error').textContent = '密码不匹配';
        return;
    }
    let urlParams = new URLSearchParams(window.location.search);
    let referredByUID = urlParams.get('ref');
    if (referredByUID === null || referredByUID === "") {
        referredByUID = localStorage.getItem("ref");
        if (referredByUID === null || referredByUID === "") {
            referredByUID = "0";
        }
    }
    console.log(userAccount);
    fetch(registerURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userAccount": userAccount,
            "userPassword": userPassword,
            "referredByUID": referredByUID,
        }),
    })
        .then((response) => {
            if (response.status === 201) {
                alert('注册成功，请返回登录');
                showLoginPage();
            } else if (response.status === 400 || response.status === 500) {
                return response.json().then((result) => {
                    const errorMessage = result.error || result.message || '未知错误';
                    alert('注册失败：' + errorMessage);
                    document.getElementById('register-error').textContent = errorMessage;
                });
            } else {
                alert('发生错误，请稍后重试');
            }
        })
        .catch(() => {
            document.getElementById("recharge-message").innerText = "服务器错误，请稍后重试";
        });
}

// 开始就执行的函数
function start() {
    console.log("start");
    let urlParams = new URLSearchParams(window.location.search);
    let referredByUID = urlParams.get('ref');
    localStorage.setItem("ref", referredByUID);
    console.log("referred By UID: ", referredByUID);

}

//加载页面完成后 就执行start函数
window.onload = start;
