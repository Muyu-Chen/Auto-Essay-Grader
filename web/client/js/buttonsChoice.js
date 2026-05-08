function clearAllActive() {
    // 获取所有具有 'uniform-button' 类的按钮
    const buttons = document.querySelectorAll('.uniform-button');
    console.log("clear buttons active class");
    // 遍历所有按钮并移除 'active' 类
    buttons.forEach(btn => btn.classList.remove('active'));
}

function selectModel(selectedButton) {
    // 获取所有按钮
    const buttons = document.querySelectorAll('.uniform-button');

    // 移除其他按钮的 active 状态
    clearAllActive();

    // 给当前点击的按钮添加 active 状态
    selectedButton.classList.add('active');

    const model_id = selectedButton.id;
    console.log(`selected button: ${model_id}`);
    let model_selected = "qwen-plus";
    if (model_id === 'model-button-1') {
        model_selected = "qwen-max";
    }
    else if (model_id === 'model-button-2'){
        model_selected = "qwen-plus";
    }
    else if (model_id === 'model-button-3'){
        model_selected = "qwen-turbo";
    }
    localStorage.setItem("model", model_selected);
    console.log(`selected model: ${model_selected}`);
}