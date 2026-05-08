const uploadFileUrl = `${window.AEG_API_BASE || "http://127.0.0.1:5000"}/upload`;
const ALLOWED_TYPES = [
    'text/csv',                // CSV 文件
    'application/vnd.ms-excel', // XLS 文件
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' // XLSX 文件
];
const MAX_FILE_SIZE_MB = 5; // 文件大小限制（MB）
const MAX_FILE_COUNT = 2; // 最大上传文件数
let selectedFiles = []; // 用于存储拖入或选择的文件
let fileNameDisplayInitialized = false; // 避免重复绑定事件

// 多语言支持
const LANGUAGE_TEXTS = {
    en: {
        dropPrompt: 'Drag and drop files here or click to select files',
        unsupportedType: 'Unsupported file type',
        fileTooLarge: 'File size exceeds the maximum limit',
        retryUpload: 'Retry upload?',
        uploadFailed: 'File upload failed',
        tooManyFiles: `Maximum ${MAX_FILE_COUNT} files allowed`,
    },
    zh: {
        dropPrompt: '拖动文件到此处或点击选择文件',
        unsupportedType: '不支持的文件类型',
        fileTooLarge: `文件过大，最大支持 ${MAX_FILE_SIZE_MB}MB`,
        retryUpload: '是否重试上传？',
        uploadFailed: '文件上传失败',
        tooManyFiles: `最多只能上传 ${MAX_FILE_COUNT} 个文件`,
    },
};
let currentLang = 'zh'; // 当前语言设置

function getText(key) {
    return LANGUAGE_TEXTS[currentLang][key];
}

// 获取拖放区域和提交按钮
let dropArea = document.getElementById('drop-area');
let submitButton = document.getElementById('submit-button');
const fileElem = document.getElementById('fileElem'); // 获取文件选择器

// 阻止默认行为
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// 添加样式反馈
['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight'), false);
});
['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false);
});

// 处理拖放文件
dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    let dt = e.dataTransfer;
    let files = dt.files;

    handleFiles(files);
}

// 校验文件类型和大小
function validateFile(file) {
    if (!ALLOWED_TYPES.includes(file.type)) {
        alert(`${getText('unsupportedType')}: ${file.type}`);
        return false;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        alert(getText('fileTooLarge'));
        return false;
    }
    return true;
}

// 处理文件列表
function handleFiles(files) {
    if (files.length === 0) return; // 如果没有文件，直接返回

    let validFiles = [...files].filter(validateFile); // 校验文件

    // 如果新选文件超出上限，移除多余文件
    if (validFiles.length + selectedFiles.length > MAX_FILE_COUNT) {
        const allowedSlots = MAX_FILE_COUNT - selectedFiles.length;
        alert(getText('tooManyFiles'));
        validFiles = validFiles.slice(0, allowedSlots); // 只保留允许的文件
    }

    validFiles.forEach(file => {
        if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            selectedFiles.push(file); // 避免重复文件
        }
    });

    updateFileNameDisplay(selectedFiles); // 显示所有文件名

    // 如果达到文件上限，禁用文件选择器
    if (selectedFiles.length >= MAX_FILE_COUNT) {
        fileElem.disabled = true;
    }
}

// 更新文件名显示
function updateFileNameDisplay(files) {
    const fileNameDisplay = dropArea.querySelector('p');

    if (files === null || files.length === 0) {
        fileNameDisplay.textContent = getText('dropPrompt');
    } else {
        fileNameDisplay.innerHTML = files.map((file, index) =>
            `<div>${file.name} <img src='delete-icon.png' alt='Delete' style='cursor: pointer;height: 13px; width: auto;' onclick='removeFile(event, ${index})'></div>`
        ).join('');
    }

    // 避免重复绑定事件
    if (!fileNameDisplayInitialized) {
        fileNameDisplay.addEventListener('click', (e) => {
            if (!e.target.matches('img')) { // 避免冲突
                document.getElementById('fileElem').click();
            }
        });
        fileNameDisplayInitialized = true;
    }
}

// 删除文件
function removeFile(event, index) {
    event.stopPropagation(); // 防止触发父元素事件
    selectedFiles.splice(index, 1); // 删除指定文件
    updateFileNameDisplay(selectedFiles); // 更新显示

    // 如果删除文件后未达到上限，启用文件选择器
    if (selectedFiles.length < MAX_FILE_COUNT) {
        fileElem.disabled = false;
    }
}

// 上传文件，支持进度显示
function uploadFile(file, isDisabled) {
    return new Promise((resolve, reject) => {
        let formData = new FormData();
        formData.append('file', file);

        const userAccount = localStorage.getItem("userAccount");
        const userPassword = localStorage.getItem("userPassword");
        const essayPrompt = document.getElementById("essayPrompt").value;
        formData.append("userAccount", userAccount);
        formData.append("userPassword", userPassword);

        //存储题目和评分标准，这两个在下一步要传给后端
        //存储列和表
        const col = document.getElementById("col-name").value;
        const table = document.getElementById("sheet-name").value;
        if (col) {
            localStorage.setItem("colName", col);
        }
        else {
            localStorage.setItem("colName", "B");
        }
        if (table) {
            localStorage.setItem("sheetName", table);
        }
        else {
            localStorage.setItem("sheetName", "1");
        }
        localStorage.setItem("essayPrompt", essayPrompt);
        //formData.append("essayPrompt", essayPrompt);
        let essayCriteria;
        if (isDisabled) {
            essayCriteria = "None";
        }
        else {
            essayCriteria = document.getElementById("switch-check").value;
        }
        localStorage.setItem("essayCriteria", essayCriteria);
        //formData.append("essayCriteria", essayCriteria);



        let xhr = new XMLHttpRequest();
        xhr.open('POST', uploadFileUrl);

        // 上传进度事件
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                let percentComplete = Math.round((e.loaded / e.total) * 100);
                console.log(`上传进度: ${percentComplete}%`);
                // 可以在这里更新UI中的进度条
            }
        });

        xhr.onload = () => {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.error) {
                        console.error('上传错误:', response.error);
                        alert(getText('uploadFailed'));
                        reject(new Error(response.error));
                    } else {
                        console.log('上传成功:', response.message);
                        console.log('文件全名:', response.fileID);
                        console.log('文件 ID :', response.fileIDName);
                        // 保存 fileID 到 localStorage
                        localStorage.setItem("fileID", response.fileIDName);
                        localStorage.setItem("fileFullName", response.fileID);
                        localStorage.setItem("isProcessing", "true");
                        successUpload(response.fileIDName);
                        resolve(response);
                    }
                } catch (e) {
                    console.error('解析响应失败:', e);
                    alert(getText('uploadFailed'));
                    reject(e);
                }
            } else {
                alert(getText('uploadFailed'));
                if (confirm(getText('retryUpload'))) {
                    uploadFile(file);
                } else {
                    reject(new Error('上传失败，状态码: ' + xhr.status));
                }
            }
        };

        xhr.onerror = () => {
            alert(getText('uploadFailed'));
            if (confirm(getText('retryUpload'))) {
                uploadFile(file).then(resolve).catch(reject); // 重试
            } else {
                reject();
            }
        };

        xhr.send(formData);
    });
}

// 提交文件
submitButton.addEventListener('click', async () => {
    const checkInputPlace2 = document.getElementById('switch-check');
    let isDisabled = checkInputPlace2.disabled;
    submitButton.disabled = true; // 禁用按钮，防止重复提交

    const essayPrompt = document.getElementById("essayPrompt").value;

    if (isDisabled) {
        console.log("评分标准已禁用");
        console.log("essayPrompt: ", essayPrompt);
        if (!essayPrompt) {
            alert('请填写题目！');
            submitButton.disabled = false; // 重新启用按钮
            return;
        }
    }
    else {
        console.log("评分标准未禁用");
        const essayCriteria = checkInputPlace2.value;
        console.log("essayCriteria: ", essayCriteria);
        if (!essayPrompt || !essayCriteria) {
            alert('请填写题目和评分标准！');
            submitButton.disabled = false; // 重新启用按钮
            return;
        }
    }

    if (selectedFiles.length === 0) {
        alert('没有文件可上传！');
        submitButton.disabled = false; // 没有文件时重新启用按钮
        return;
    }
    // 目前只上传单个文件，可以扩展为多文件上传
    for (const file of selectedFiles) {
        try {
            // todo：对文件进行处理，但是目前应该不需要
            await uploadFile(file); // 逐个文件上传，确保每个文件只上传一次
        } catch (error) {
            console.error('文件上传失败:', file.name);
            console.error(error);
        }
    }
    // 上传完成后的逻辑
    selectedFiles = []; // 清空已选文件
    updateFileNameDisplay(selectedFiles); // 清空文件显示
    fileElem.disabled = false; // 重新启用文件选择器
    fileElem.value = ''; // 重置文件选择器的值
    submitButton.disabled = false; // 上传完成后重新启用按钮
});

// 文件选择器逻辑
document.getElementById('fileElem').addEventListener('change', (e) => {
    handleFiles(e.target.files); // 调用与拖放相同的逻辑
});
