async function successUpload() {
    console.log("上传成功, 开始处理文件...");
    const fileIDName = localStorage.getItem("fileID");
    console.log("fileIDName: ", fileIDName);

    if (!fileIDName) {
        console.warn("No file ID found in localStorage.");
        return;
    }

        // Lock UI: Disable sidebar and main page, show loading animation
    const sidebar = document.getElementById("sidebar");
    const mainPage = document.getElementById("main-page");
    
    if (sidebar && mainPage) {
        sidebar.style.pointerEvents = "none"; // Disable interactions
        sidebar.style.opacity = "0.5"; // Dim the sidebar
        mainPage.style.pointerEvents = "none"; // Disable interactions
        mainPage.style.opacity = "0.5"; // Dim the main page
    }
    
    const overlay = document.createElement("div");
    overlay.id = "overlay";
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
    overlay.style.zIndex = "999";
    document.body.appendChild(overlay);
    
    const loadingAnimation = document.createElement("div");
    loadingAnimation.id = "loading-animation";
    loadingAnimation.style.position = "fixed";
    loadingAnimation.style.top = "50%";
    loadingAnimation.style.left = "50%";
    loadingAnimation.style.transform = "translate(-50%, -50%)";
    loadingAnimation.style.zIndex = "1000";
    loadingAnimation.innerHTML = `
        <div style="text-align: center;">
            <div class="spinner" style="width: 50px; height: 50px; border: 5px solid rgba(0, 0, 0, 0.1); border-top: 5px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <p style="color: white; font-size: 18px;">正在处理，请稍候...</p>
            <p style="color: white; font-size: 18px;">请勿刷新界面</p>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    document.body.appendChild(loadingAnimation);

    // Update localStorage to reflect processing state
    localStorage.setItem("isProcessing", "true");
    userAccount = localStorage.getItem("userAccount");
    try {
        // Send file ID to backend for processing
        console.log("Initiating file processing...");
        const initiateResponse = await fetch(processFileURL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "fileID": fileIDName,
                "fileFullName": localStorage.getItem("fileFullName"),
                "isProcessing": "true",
                "userAccount": userAccount,
                "userPassword": localStorage.getItem("userPassword"),
                "essayPrompt": localStorage.getItem("essayPrompt"),
                "essayCriteria": localStorage.getItem("essayCriteria"),
                "sheetName": localStorage.getItem("sheetName"),
                "colName": localStorage.getItem("colName"),
                "model": localStorage.getItem("model"),
             }),
        });
        console.log("initiateResponse: ", initiateResponse);
        console.log("initiateResponse.ok: ", initiateResponse.ok);
        
        if (!initiateResponse.ok) {
            throw new Error(`Error: ${initiateResponse.statusText}`);
        }

        console.log("Processing started. Polling for status...");

        // Poll the backend every 5 seconds to check the processing status
        const pollInterval = 10000; // 5 seconds
        const maxRetries = 180; // Poll for up to 30 minutes
        let retries = 0;
        let isComplete = false;

        while (!isComplete && retries < maxRetries) {
            console.log(`Polling attempt ${retries + 1}...`);
            await new Promise((resolve) => setTimeout(resolve, pollInterval));
            retries += 1;

            const statusResponse = await fetch(`${checkStatusURL}?userAccount=${userAccount}&fileID=${fileIDName}`, {
                method: 'GET',
            });

            if (!statusResponse.ok) {
                console.warn(`Status check failed: ${statusResponse.statusText}`);
                continue;
            }

            const statusResult = await statusResponse.json();
            console.log("Status response:", statusResult);

            if (statusResult.complete === "true") {
                console.log("Processing complete:", statusResult);
                isComplete = true;

                // 获取下载链接
                const downloadLink = statusResult.downloadLink;
                if (downloadLink) {
                    console.log("Download link:", downloadLink);
                    // 自动下载
                    const a = document.createElement('a');
                    a.href = downloadLink;
                    a.download = ''; // 可以设置下载文件的默认名称
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    // 显示弹窗：若未自动下载，请点击此处下载
                    alert("若未自动下载，请点击此处下载: " + downloadLink);
                    // 你可以在这里处理下载链接，例如显示在UI上

                    const overlay = document.getElementById("overlay");
                    if (overlay) {
                        document.body.removeChild(overlay);
                    }
                    
                } else {
                    console.warn("Download link not found in the response.");
                }
            }
        }

        if (!isComplete) {
            throw new Error("Processing timed out. Please try again later.");
        }

        // Update processing status in localStorage
        localStorage.setItem("isProcessing", "false");
        alert("文件处理完成！");
    } catch (error) {
        console.error("Error during file processing:", error);
        alert("文件处理失败，请稍后重试。");
    } finally {
        // Unlock UI and remove loading animation
        if (sidebar && mainPage) {
            sidebar.style.pointerEvents = "auto";
            sidebar.style.opacity = "1";
            mainPage.style.pointerEvents = "auto";
            mainPage.style.opacity = "1";
        }

        const loadingElement = document.getElementById("loading-animation");
        if (loadingElement) {
            document.body.removeChild(loadingElement);
        }
    }
    // 根据fileID请求后台对文件进行操作
    // 封锁前台，禁止操作前台
    // 显示等待动画
    // 解锁isProcessing（给localsotage修改，随后发送给后台让后台修改）
}