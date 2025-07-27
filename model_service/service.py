from flask import Flask, render_template, request, jsonify
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
from transformers.generation import GenerationConfig
import os

device5 = torch.device("cuda:0")
device6 = torch.device("cuda:1")
device7 = torch.device("cuda:2")

############################### Baichuan2-13B ###############################
MODEL_PATH_BAICHUAN = "/home/duansf/models/Baichuan2-13B-Chat"

tokenizer_baichuan = AutoTokenizer.from_pretrained(MODEL_PATH_BAICHUAN, use_fast=False, trust_remote_code=True)
model_baichuan = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH_BAICHUAN, torch_dtype=torch.float16, trust_remote_code=True
).quantize(4).to(device5)  # Ensure model is moved to device0
model_baichuan.generation_config = GenerationConfig.from_pretrained(MODEL_PATH_BAICHUAN)

def generate_response_baichuan(input_text):
    messages = [{"role": "user", "content": input_text}]
    response_baichuan = model_baichuan.chat(tokenizer_baichuan, messages)
    return response_baichuan

############################### Qwen-7B ###############################
MODEL_PATH_QWEN = '/home/duansf/models/Qwen/Qwen-7B-Chat'

tokenizer_qwen = AutoTokenizer.from_pretrained(MODEL_PATH_QWEN, trust_remote_code=True, resume_download=True)
model_qwen = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH_QWEN, torch_dtype=torch.float16, trust_remote_code=True, resume_download=True
).eval().to(device6)  # Ensure model is moved to device7
config_qwen = GenerationConfig.from_pretrained(MODEL_PATH_QWEN, trust_remote_code=True, resume_download=True)

def generate_response_qwen(input_text):
    # history = []
    # with torch.no_grad():
    #     response_qwen = ""
    #     for response_qwen in model_qwen.chat_stream(tokenizer_qwen, input_text, history=history, generation_config=config_qwen):
    #         pass
    # return response_qwen
    # tokenized_inputs = tokenizer_qwen([input_text], return_tensors="pt").to(device6)
    # input_length = tokenized_inputs["input_ids"].shape[1]
    # generated_ids = model_qwen.generate(**tokenized_inputs, max_new_tokens=100)
    # output = tokenizer_qwen.batch_decode(generated_ids[:, input_length:], skip_special_tokens=True)[0]
    # return output
    response, history = model_qwen.chat(tokenizer_qwen, input_text, history=None)
    return response


############################### ChatGLM ###############################
# MODEL_PATH_CHATGLM = "/home/rookiexxy/model_chatglm_6b"


# tokenizer_chatglm = AutoTokenizer.from_pretrained(MODEL_PATH_CHATGLM, trust_remote_code=True)
# model_chatglm = AutoModel.from_pretrained(MODEL_PATH_CHATGLM, trust_remote_code=True).half().to(device7)
# model_chatglm = model_chatglm.eval()

# def generate_response_chatglm(input_text):
#     history = []
#     response_chatglm = ""
#     with torch.no_grad():
#         for partial_response, history in model_chatglm.stream_chat(tokenizer_chatglm, input_text, history=history, max_new_tokens=512):
#             response_chatglm += partial_response
#     return partial_response

# ############################## InternLM ##############################
# MODEL_PATH_INTERN = "/home/rookiexxy/InternLM2_5"

# # InternLM 使用 GPU 7
# os.environ["CUDA_VISIBLE_DEVICES"] = "7"
# tokenizer_intern = AutoTokenizer.from_pretrained(MODEL_PATH_INTERN, trust_remote_code=True)
# model_intern = AutoModelForCausalLM.from_pretrained(
#     MODEL_PATH_INTERN, device_map="auto", trust_remote_code=True, torch_dtype=torch.float16
# )
# model_intern.eval()

# def generate_response_intern(input_text):
#     response_intern = model_intern.chat(tokenizer_intern, input_text, history=[])
#     return response_intern



############################### Flask 应用 ###############################
app = Flask(__name__, static_folder="static")

@app.route('/', methods=['POST'])
def process_request():
    data = request.json  # 获取第一台服务器传来的数据
    task = data.get('task', "")
    module_value = data.get('module_value', '')
    prompt_value = data.get('prompt_value', '')
    template_value = data.get('template_value', '')
    # 调用相应的大模型处理
    # 根据选择的模型调用对应的生成函数
    print(task)
    print(module_value)
    print(prompt_value)
    print(template_value)
    if module_value == "Baichuan2-13B":
        if task=="jail":
            result1 = generate_response_baichuan(prompt_value)
            result2 = generate_response_baichuan(f"{template_value} {prompt_value}")
            return jsonify({"result1": result1, "result2": result2})
        elif task=="mind":
            result = generate_response_baichuan(template_value)
            return jsonify({"result": result})
        else:
            result = generate_response_baichuan(prompt_value+"\n请直接从以下四个选项中选出你的答案\n"+template_value)
            return jsonify({"result": result})

    elif module_value == "Qwen-7B":
        if task=="jail":
            result1 = generate_response_qwen(prompt_value)
            result2 = generate_response_qwen(f"{template_value} {prompt_value}")
            return jsonify({"result1": result1, "result2": result2})
        elif task=="mind":
            result = generate_response_qwen(template_value)
            return jsonify({"result": result})
        else:
            result = generate_response_qwen(prompt_value+"\n请直接从以下四个选项中选出你的答案\n"+template_value)
            return jsonify({"result": result})
        
    else:
        if task=="jail":
            result1 = "选择的模型无效"
            result2 = "选择的模型无效"
            return jsonify({"result1": result1, "result2": result2})
        elif task=="mind":
            return jsonify({"result": "选择的模型无效"})
        else:
            return jsonify({"result": "选择的模型无效"})
            
            
    

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
