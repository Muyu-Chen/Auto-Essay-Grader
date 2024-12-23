let token = "";

function login() {
    const userPhone = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    console.log(userPhone);
    fetch("http://localhost:5000/login", {
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
    fetch("http://localhost:5000/charge", {
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
                document.getElementById("balance").innerText = data.currentBalance;}
        })
        .catch(() => {
            document.getElementById("balance").innerText = "获取失败";
        });
}

function charge() {
    const cardCode = document.getElementById("card-code").value;
    const userPhone = localStorage.getItem("userPhone");
    const userPassword = localStorage.getItem("userPassword");
    fetch("http://127.0.0.1:5000/charge", {
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
