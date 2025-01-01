// change the URL to your own server URL
const loginURL = "http://localhost:5000/login";
const chargeURL = "http://localhost:5000/charge";
const registerURL = "http://localhost:5000/register";

function login() {
    const userPhone = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    console.log(userPhone);
    fetch(loginURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userPhone": userPhone,
            "userPassword": password,
            "todo": "isAuthurized",
        }),
    })
        .then((response) => {
            if (response.status === 200) {
                console.log("here is 200");
                localStorage.setItem("userPhone", userPhone); // 保存 userID 到 localStorage
                localStorage.setItem("userPassword", password); // 保存 userID 到 localStorage
                document.getElementById("login-page").style.display = "none";
                document.getElementById("recharge-page").style.display = "block";
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
                document.getElementById("login-error").innerText = "服务器错误，请稍后重试";
            }
        });
}

function getBalance() {
    console.log("here in getBalance");
    const userPhone = localStorage.getItem("userPhone");
    const userPassword = localStorage.getItem("userPassword");
    console.log(userPhone);
    fetch(chargeURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userPhone": userPhone,
            "userPassword": userPassword,
            "todo": "getBalance",
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.currentBalance !== undefined) {
                document.getElementById("balance").innerText = data.currentBalance;
            }
        })
        .catch(() => {
            document.getElementById("balance").innerText = "获取失败";
        });
}

function charge() {
    const cardCode = document.getElementById("card-code").value;
    const userPhone = localStorage.getItem("userPhone");
    const userPassword = localStorage.getItem("userPassword");
    fetch(chargeURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userPhone": userPhone,
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

// 显示注册页面
function showRegisterPage() {
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('register-page').style.display = 'block';
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
    const userPhone = document.getElementById('register-username').value;
    const userPassword = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;

    if (userPassword !== confirmPassword) {
        document.getElementById('register-error').textContent = '密码不匹配';
        return;
    }
    console.log(username);
    fetch(registerURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "userPhone": userPhone,
            "userPassword": userPassword
        }),
    })
        .then((response) => {
            if (response.status === 201) {
                alert('注册成功，请返回登录');
                showLoginPage();
            } else if (response.status === 400 || response.status === 500) {
                alert('注册失败：' + result.message);
            } else {
                alert('发生错误，请稍后重试');
            }
        })
        .catch(() => {
            document.getElementById("recharge-message").innerText = "服务器错误，请稍后重试";
        });
}