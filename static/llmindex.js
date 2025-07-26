function start_detect_llm(){
    var data = {
      "module_value" : document.getElementById("module_choose").value,  //目前只上传模型名，后端去特定路径下寻找模型。之后需要用户上传模型文件，后端接收并评测
      "prompt_value" : document.getElementById("prompt_choose").value,
      "template_value" : document.getElementById("template_choose").value
    }
  
  fetch('/llm_detect', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(handleResponse)
  .catch(error => {
    console.error('发生错误:', error);
  });
  }

  function typeWriter(text, index, outputArea) {
    if (index < text.length) {
        outputArea.value += text.charAt(index);
        setTimeout(function() {
            typeWriter(text, index + 1, outputArea);
        }, 100); // 调整时间间隔来加快或减慢打字速度
    }
}
  
  function handleResponse(data) {
    console.log('收到来自服务器的响应:', data);
    data = data["result"]
    // 这里对服务器的响应进行进一步处理，展示llm回答结果
    var outputArea1 = document.querySelector('textarea[placeholder="输出文本1"]');
    var outputArea2 = document.querySelector('textarea[placeholder="输出文本2"]');

    outputArea1.value = ''; // 清空 outputArea1
    outputArea2.value = ''; // 清空 outputArea2
    typeWriter(data["result1"], 0, outputArea1); // 显示获取的llm的回答
    typeWriter(data["result2"], 0, outputArea2);

    
  }
  
  function handleError(error) {
    console.error('发生错误:', error);
    // 这里可以处理发生的错误
    alert("检测失败，请重新检测！")
  }