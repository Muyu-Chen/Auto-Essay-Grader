
document.addEventListener('DOMContentLoaded', function () {
    // 获取复选框元素
    const toggleSwitch = document.getElementById('essay-switch');
    const checkInputPlace = document.getElementById('switch-check');
    // 监听复选框的变化事件
    toggleSwitch.addEventListener('change', function () {
        if (this.checked) {
            console.log('滑块位置：开启');
            checkInputPlace.disabled = true;
            checkInputPlace.placeholder = '使用默认模板，输入已禁用';

        } else {
            console.log('滑块位置：关闭');
            checkInputPlace.disabled = false;
            checkInputPlace.placeholder = '评分标准：“强烈”建议打开开关，使用默认模板。若需要修改，请在默认模板的基础上修改。不要随意自行发挥，否则会造成每一篇的评分标准均不一致。';
        }
    });

    // 如果需要立即获取初始状态
    checkTogglePosition(toggleSwitch);
});

// 定义一个函数来检查滑块位置
function checkTogglePosition(switchElement) {
    if (switchElement.checked) {
        console.log('当前滑块位置：开启');
    } else {
        console.log('当前滑块位置：关闭');
    }
}

function startFunc() {
    const userAccount = localStorage.getItem("userAccount");
    const userPassword = localStorage.getItem("userPassword");
    console.log("userAccount: ", userAccount);
    console.log("userPassword: ", userPassword);
    getBalanceMainPage();

}

function logout() {
    localStorage.removeItem("userAccount"); // 清空 userAccount
    localStorage.removeItem("userPassword"); // 清空 userPassword
    localStorage.removeItem("userPhone");
    localStorage.removeItem("UID");
    window.location.href = loginPage; // 将 "register.html" 替换为你的注册页面链接
}


function getBalanceMainPage() {
    console.log("here in getBalance in mainpageJS.js");
    const userAccount = localStorage.getItem("userAccount");
    const userPassword = localStorage.getItem("userPassword");
    console.log(userAccount);
    if (userAccount === null || userPassword === null) {
        console.error("无账号密码，请重新登录");
        //调试时注释掉，记得取消注释
        //alert("无法识别账号密码，请重新登录");
        //window.location.href = loginPage;
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
                let balance = parseFloat(data.currentBalance).toFixed(3);
                console.log("(in mainpageJS) balance: ", balance);
                document.getElementById("balance").innerText = balance;
                localStorage.setItem("balance", data.currentBalance);
                // 网络正常，可以去获取是否有待处理的文件
                getProcessing();
            }
        })
        .catch((error) => {
            console.error("网络错误:", error);
            document.getElementById("balance").innerText = "Network error, loading...";
            // 休眠2n秒
            timeDeley += 2000; // 增加休眠时间
            console.log("time deley: ", timeDeley);
            setTimeout(() => { getBalanceMainPage(); }, timeDeley);
        });
}

function getProcessing() {
    console.log("here in getProcessing in mainpageJS.js");
    isProcessingLocal = localStorage.getItem("isProcessing");
    console.log("isProcessingLocal: ", isProcessingLocal);
    
        const userAccount = localStorage.getItem("userAccount");
        const userPassword = localStorage.getItem("userPassword");
        fetch(getDataURL + `?userAccount=${encodeURIComponent(userAccount)}&userPassword=${encodeURIComponent(userPassword)}&todo=isProcessing`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("isProcessing: ", data);
            
                if (data.isProcessing === "true") {
                    console.log("有待处理文件");
                    if (isProcessingLocal === "false" || isProcessingLocal === null || isProcessingLocal === "") {
                        alert("有待处理文件，请先等待处理完再上传新文件");
                    }
                    const submitButton = document.getElementById("submit-button");
                    submitButton.disabled = true;
                    document.getElementById("isprocessing").innerText = "有待处理文件，请等待。处理完成后会自动下载。";
                    document.getElementById("isprocessing").style.color = "red";
                }
                else if (data.isProcessing === "false" || data.isProcessing === "") {
                    console.log("没有待处理文件");
                    const submitButton = document.getElementById("submit-button");
                    submitButton.disabled = false;
                    document.getElementById("isprocessing").innerText = "没有待处理文件";
                    document.getElementById("isprocessing").style.color = "green";
                }
            }
        
            )
            .catch((error) => {
                console.error("网络错误:", error);
                document.getElementById("isprocessing").innerText = "Network error, loading...";
                // 休眠2n秒
                timeDeley += 2000; // 增加休眠时间
                console.log("time deley: ", timeDeley);
                setTimeout(() => { getProcessing(); }, timeDeley);
            });
    
}



window.addEventListener('load', startFunc);
