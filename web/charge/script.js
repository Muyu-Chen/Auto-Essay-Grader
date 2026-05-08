const API_BASE = window.AEG_API_BASE || "http://127.0.0.1:5000";
const loginURL = `${API_BASE}/login`;
const chargeURL = `${API_BASE}/charge`;
const registerURL = `${API_BASE}/register`;
const getDataURL = `${API_BASE}/getData`;

const chargePage = "./verified.html";

function login() {
    const userAccount = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    console.log(userAccount);
    console.log(password);
    fetch(loginURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userAccount": userAccount,
            "userPassword": password,
            "todo": "isVerified",
        }),
    })
        .then((response) => {
            if (response.status === 200) {
                console.log("here is 200");
                localStorage.setItem("userAccount", userAccount); // 保存 userID 到 localStorage
                localStorage.setItem("userPassword", password); // 保存 userID 到 localStorage
                document.getElementById("login-page").style.display = "none";
                document.getElementById("recharge-page").style.display = "block";
                //window.location.href = chargePage;
                console.log("here before getBalance");
                getBalance();

            } else {
                throw new Error('登录失败');
            }
        })
        .catch((error) => {
            if (error.message === '登录失败') {
                document.getElementById("login-error").innerText = "登录失败，请检查账号密码";
            } else {
                console.log(error);
                document.getElementById("login-error").innerText = "服务器错误，请稍后重试";
            }
        });
}

function getBalance() {
    console.log("here in getBalance");
    const userAccount = localStorage.getItem("userAccount");
    const userPassword = localStorage.getItem("userPassword");
    let userBalance = 0;
    console.log(userAccount);

    fetch(getDataURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userAccount": userAccount,
            "userPassword": userPassword,
            "todo": "getBalance",
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.currentBalance !== undefined) {
                userBalance = data.currentBalance;
                console.log(userBalance);
                document.getElementById("balance").innerText = userBalance;

            }
        })
        .catch(() => {
            document.getElementById("balance").innerText = "获取失败";
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
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('register-page').style.display = 'block';
}

function showLoginPage() {
    document.getElementById('register-page').style.display = 'none';
    document.getElementById('login-page').style.display = 'block';
}

async function register() {
    const userAccount = document.getElementById('register-username').value;
    const userPassword = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    if (userAccount === "" || userPassword === "" || confirmPassword === "") {
        document.getElementById('register-error').textContent = '请填写完整信息';
        return;
    }
    if (userPassword !== confirmPassword) {
        document.getElementById('register-error').textContent = '密码不匹配';
        return;
    }
    let urlParams = new URLSearchParams(window.location.search);
    let referredByUID = urlParams.get('ref');
    if (referredByUID === null || referredByUID === "") {
        referredByUID = localStorage.getItem("ref");
        if (referredByUID === null || referredByUID === "") {
            console.log("local ref UID is null")
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
                response.json().then(result => {
                    const errorMessage = result.error || result.message || '未知错误';
                    alert('注册失败：' + errorMessage);
                    console.log(errorMessage);
                    document.getElementById('register-error').textContent = errorMessage;
                }).catch(() => {
                    alert('注册失败：无法解析服务器响应');
                });
            } else {
                alert('发生错误，请稍后重试');
            }
        })
        .catch(() => {
            document.getElementById("recharge-message").innerText = "服务器错误，请稍后重试";
        });
}



function start() {
    console.log("start");
    let urlParams = new URLSearchParams(window.location.search);
    let referredByUID = urlParams.get('ref');
    localStorage.setItem("ref", referredByUID);
    console.log("referred By UID: ", referredByUID);

    const pageId = document.documentElement.id;
    console.log(pageId);
    // 根据页面 ID 执行特定函数
    if (pageId === 'page-verifed') {
        getBalance();
    }
}

window.onload = start;
