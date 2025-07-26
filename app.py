from flask import Flask, render_template, request, jsonify
import threading
from EvaluationConfig import *
#from EvaluationPlatformNEW import *
import time
import requests
import re

# 开一个终端，并建立ssh端口转发命令
# ssh -i "/home/ai-defender/AI-Defender/id_rsa_ai_defender" -L 6000:127.0.0.1:5000 ai-defender@47.117.171.217 -p 9530
# ssh -i "/home/unicorn/.ssh/id_rsa_ai_defender" -L 6000:127.0.0.1:5000 ai-defender@47.117.171.217 -p 9530
# llm服务器的本地转发地址
SECOND_SERVER_URL = "http://127.0.0.1:5000"

def wait():
    time.sleep(150)

def go():
    ModelEvaluation(new_evalueation_params)

app = Flask(__name__, static_url_path='/static') # 指定静态文件路径



@app.route('/')
def login():
    return render_template('Login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register')
def register():
    return render_template('Register.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/llm_believable_test', methods=["GET", "POST"])  # llm可信测试
def llm_believable_test():
    if request.method == "POST":
        # 获取用户选择的数据
        module_value = request.form.get("module_choose", "").strip()    #获取用户的模型选择
        prompt_value = request.form.get("prompt_choose", "").strip()    #获取用户的问题选择
        
        # 2. 处理自定义问题优先级 (自定义 > 预设)
        custom_prompt = request.form.get("prompt_input", "").strip()    #用户是否自定义了输入
        prompt_value = custom_prompt if custom_prompt else prompt_value

        # 4. 验证必填字段
        if not module_value:
            flash("必须选择模型", "error")
            return render_template("llmindex.html", result=default_result)
            
        if not prompt_value:
            flash("必须输入或选择问题", "error")
            return render_template("llmindex.html", result=default_result)

        
        # 构造发送到 5000 端口的 JSON 数据
        payload = {
            "task":"jail",
            "module_value": module_value,
            "prompt_value": prompt_value,
        }
        print(payload)
        try:
            # 发送 HTTP POST 请求到本机 6000 端口
            response = requests.post(SECOND_SERVER_URL, json=payload)

            # 获取返回的结果
            result = response.json()
            print(result)

        except requests.exceptions.RequestException as e:
            answer = f"Error communicating with service: {e}"
            result = {
                "result1":"LLM服务已暂停运行，请联系工作人员开启后进行评测！",
                "result2":"LLM服务已暂停运行，请联系工作人员开启后进行评测！"
            }

        result['model'] = module_value
        result['select_prompt'] = request.form.get("prompt_choose")
        result['type_prompt'] = request.form.get("prompt_input")
        result['select_template'] = request.form.get("template_choose")
        result['type_template'] = request.form.get("template_input")
        # 返回结果页面
        
        return render_template("llm_believable_test.html", result=result)


    # 默认显示输入页面
    result={
        'model':"",
        'select_prompt':"",
        'type_prompt':"",
        'select_template':"",
        "type_template":"",
        "result1":"",
        "result2":""}
    return render_template("llm_believable_test.html", result=result)



@app.route('/llmindex', methods=["GET", "POST"])
def llmindex():
    # 初始化默认返回值
    default_result = {
        'model': "",                        
        'select_prompt': "",                #输入、选择问题
        'type_prompt': "",                  #自定义输入问题
        'select_template': "",              #选择输入攻击模板
        'type_template': "",                #自定义攻击模板
        'result1': "",
        'result2': ""
    }

    if request.method == "POST":
        # 1. 获取并清洗表单数据
        module_value = request.form.get("module_choose", "").strip()
        prompt_value = request.form.get("prompt_choose", "").strip()
        template_value = request.form.get("template_choose", "").strip()
        
        # 2. 处理自定义问题优先级 (自定义 > 预设)
        custom_prompt = request.form.get("prompt_input", "").strip()
        prompt_value = custom_prompt if custom_prompt else prompt_value
        
        # 3. 处理自定义模板优先级 (自定义 > 预设)
        custom_template = request.form.get("template_input", "").strip()
        template_value = custom_template if custom_template else template_value

        # 4. 验证必填字段
        if not module_value:
            flash("必须选择模型", "error")
            return render_template("llmindex.html", result=default_result)
            
        if not prompt_value:
            flash("必须输入或选择问题", "error")
            return render_template("llmindex.html", result=default_result)

        # 5. 构造请求负载
        payload = {
            "task": "jail",
            "module_value": module_value,
            "prompt_value": prompt_value,
            "template_value": template_value
        }
        print("[DEBUG] 发送到6000端口的负载:", payload)
        
        # 6. 调用下游服务
        try:
            response = requests.post(SECOND_SERVER_URL, json=payload)
            result = response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 服务调用失败: {e}")
            result = {
                "result1": "LLM服务通信失败，请稍后重试或联系管理员",
                "result2": "LLM服务通信失败，请稍后重试或联系管理员"
            }

        # 7. 构造返回结果
        result.update({
            'model': module_value,
            'select_prompt': request.form.get("prompt_choose", ""),
            'type_prompt': custom_prompt,
            'select_template': request.form.get("template_choose", ""),
            'type_template': custom_template
        })
        print(result)
                
        return render_template("llmindex.html", result=result)

    # GET请求返回空表单
    
    return render_template("llmindex.html", result=default_result)


@app.route('/llm_mind_test', methods=["GET", "POST"])  # 心智测试
def llm_mind_test():
    if request.method == "POST":
        # 获取用户选择的数据
        module_value = request.form.get("module_choose")            #模型选择
        prompt_value = request.form.get("prompt_choose")            #问题类型选择
        template_value = request.form.get("prompt_choose_juti")        #具体问题

        # 构造发送到 6000 端口的 JSON 数据
        payload = {
            "task":"mind",
            "module_value": module_value,
            "prompt_value": "",
            "template_value": template_value
        }
        print(payload)
        try:
            # 发送 HTTP POST 请求到本机 6000 端口
            response = requests.post(SECOND_SERVER_URL, json=payload)

            # 获取返回的结果
            result = response.json()
            print(result)

        except requests.exceptions.RequestException as e:
            answer = f"Error communicating with service: {e}"
            result = {
                "result":"LLM服务已暂停运行，请联系工作人员开启后进行评测！"
            }

        result['model'] = module_value
        result['select_prompt'] = request.form.get("prompt_choose")
        result['select_template'] = request.form.get("prompt_choose_juti")

        # 返回结果页面
        return render_template("llm_mind_test.html",
                               result=result)
    # 默认显示输入页面
    result={
        'model':"",
        'select_prompt':"",
        'select_template':"",
        "result":""}
    # 默认显示输入页面
    return render_template("llm_mind_test.html", result=result)


@app.route('/llm_ability_test_international_law', methods=["GET", "POST"])  # 国际法律
def llm_ability_test_international_law():
    if request.method == "POST":
        # 获取用户选择的数据
        module_value = request.form.get("module_choose")
        prompt_value = request.form.get("prompt_choose")
        template_value = LAW_PROMPT_OPTIONS[prompt_value]
        template_value = '\n'.join(template_value)
        print(template_value)

        # 构造发送到 6000 端口的 JSON 数据
        payload = {
            "task":"ability",
            "module_value": module_value,
            "prompt_value": prompt_value,
            "template_value": template_value
        }
        print(payload)
        try:
            # 发送 HTTP POST 请求到本机 6000 端口
            response = requests.post(SECOND_SERVER_URL, json=payload)

            # 获取返回的结果
            result = response.json()
            print(result)

        except requests.exceptions.RequestException as e:
            result = {
                "result":"LLM服务已暂停运行，请联系工作人员开启后进行评测！"
            }
        
        result['model'] = module_value
        result['select_prompt'] = request.form.get("prompt_choose")

        # 返回结果页面
        return render_template("llm_ability_test_international_law.html",
                               result=result)

    # 默认显示输入页面
    result={
        'model':"",
        'select_prompt':"",
        "result":""}
    # 默认显示输入页面
    return render_template("llm_ability_test_international_law.html", result=result)


@app.route('/llm_ability_test_logic_reasoning', methods=["GET", "POST"])  # 逻辑推理
def llm_ability_test_logic_reasoning():
    if request.method == "POST":
        # 获取用户选择的数据
        # 获取用户选择的数据
        module_value = request.form.get("module_choose")
        prompt_value = request.form.get("prompt_choose")
        template_value = LOGIC_PROMPT_OPTIONS[prompt_value]
        template_value = '\n'.join(template_value)
        print(template_value)

        # 构造发送到 6000 端口的 JSON 数据
        payload = {
            "task":"ability",
            "module_value": module_value,
            "prompt_value": prompt_value,
            "template_value": template_value
        }
        print(payload)
        try:
            # 发送 HTTP POST 请求到本机 6000 端口
            response = requests.post(SECOND_SERVER_URL, json=payload)

            # 获取返回的结果
            result = response.json()
            print(result)

        except requests.exceptions.RequestException as e:
            result = {
                "result":"LLM服务已暂停运行，请联系工作人员开启后进行评测！"
            }

        result['model'] = module_value
        result['select_prompt'] = request.form.get("prompt_choose")
        # 返回结果页面
        return render_template("llm_ability_test_logic_reasoning.html",
                               result=result)

    # 默认显示输入页面
    result={
        'model':"",
        'select_prompt':"",
        "result":""}
    # 默认显示输入页面
    return render_template("llm_ability_test_logic_reasoning.html", result=result)


@app.route('/llm_ability_test_business_ethics', methods=["GET", "POST"])  # 商业道德
def llm_ability_test_business_ethics():
    if request.method == "POST":
        # 获取用户选择的数据
        # 获取用户选择的数据
        module_value = request.form.get("module_choose")
        prompt_value = request.form.get("prompt_choose")
        template_value = BUSINESS_PROMPT_OPTIONS[prompt_value]
        template_value = '\n'.join(template_value)
        print(template_value)
        # 构造发送到 6000 端口的 JSON 数据
        payload = {
            "task":"ability",
            "module_value": module_value,
            "prompt_value": prompt_value,
            "template_value": template_value
        }
        print(payload)
        try:
            # 发送 HTTP POST 请求到本机 6000 端口
            response = requests.post(SECOND_SERVER_URL, json=payload)

            # 获取返回的结果
            result = response.json()
            print(result)

        except requests.exceptions.RequestException as e:
            result = {
                "result":"LLM服务已暂停运行，请联系工作人员开启后进行评测！"
            }
        result['model'] = module_value
        result['select_prompt'] = request.form.get("prompt_choose")
        # 返回结果页面
        return render_template("llm_ability_test_business_ethics.html",
                               result=result)
    # 默认显示输入页面
    result={
        'model':"",
        'select_prompt':"",
        "result":""}
    # 默认显示输入页面
    return render_template("llm_ability_test_business_ethics.html", result=result)


@app.route('/llm_ability_test_china_history', methods=["GET", "POST"])  # 中国历史
def llm_ability_test_china_history():
    if request.method == "POST":
        # 获取用户选择的数据
        # 获取用户选择的数据
        module_value = request.form.get("module_choose")
        prompt_value = request.form.get("prompt_choose")
        template_value = HISTORY_PROMPT_OPTIONS[prompt_value]
        template_value = '\n'.join(template_value)
        print(template_value)
        # 构造发送到 6000 端口的 JSON 数据
        payload = {
            "task":"ability",
            "module_value": module_value,
            "prompt_value": prompt_value,
            "template_value": template_value
        }
        print(payload)
        try:
            # 发送 HTTP POST 请求到本机 6000 端口
            response = requests.post(SECOND_SERVER_URL, json=payload)

            # 获取返回的结果
            result = response.json()
            print(result)

        except requests.exceptions.RequestException as e:
            result = {
                "result":"LLM服务已暂停运行，请联系工作人员开启后进行评测！"
            }

        result['model'] = module_value
        result['select_prompt'] = request.form.get("prompt_choose")
        # 返回结果页面
        return render_template("llm_ability_test_china_history.html",
                               result=result)

    # 默认显示输入页面
    result={
        'model':"",
        'select_prompt':"",
        "result":""}
    # 默认显示输入页面
    return render_template("llm_ability_test_china_history.html", result=result)


@app.route('/llm_ability_test_china_culture', methods=["GET", "POST"])  # 中国文化
def llm_ability_test_china_culture():
    if request.method == "POST":
        # 获取用户选择的数据
        # 获取用户选择的数据
        module_value = request.form.get("module_choose")
        prompt_value = request.form.get("prompt_choose")
        template_value = CULTURE_PROMPT_OPTIONS[prompt_value]
        template_value = '\n'.join(template_value)
        print(template_value)
        # 构造发送到 6000 端口的 JSON 数据
        payload = {
            "task":"ability",
            "module_value": module_value,
            "prompt_value": prompt_value,
            "template_value": template_value
        }
        print(payload)
        try:
            # 发送 HTTP POST 请求到本机 6000 端口
            response = requests.post(SECOND_SERVER_URL, json=payload)

            # 获取返回的结果
            result = response.json()
            print(result)

        except requests.exceptions.RequestException as e:
            result = {
                "result":"LLM服务已暂停运行，请联系工作人员开启后进行评测！"
            }

        result['model'] = module_value
        result['select_prompt'] = request.form.get("prompt_choose")
        # 返回结果页面
        return render_template("llm_ability_test_china_culture.html",
                               result=result)

    # 默认显示输入页面
    result={
        'model':"",
        'select_prompt':"",
        "result":""}
    # 默认显示输入页面
    return render_template("llm_ability_test_china_culture.html", result=result)



@app.route('/detect', methods=['POST'])
def detect():
    data = request.json  # 收到来自前端的数据
    print(data)
    # 处理接收到的数据，进行评测，并返回响应给前端
    global new_evalueation_params
    new_evalueation_params = evaluation_params # 根据前端用户的需求，修改评测参数
    thread = threading.Thread(target=wait) # 调用评测函数
    thread.start()
    thread.join() # 等待评测执行完成， 结果在全局变量result中
    
    response_data = result # 需要在EvaluatePlatformNew中将结果指标保存到result中，并组织成以下格式
    # response_data = {
    #     "CACC": 28,
    #     "ASR":  30,
    #     "MRTA": 50,
    #     "ACAC": 50,
    #     "ACTC": 50,
    #     "NTE": 50,
    #     "ALDP": 50,
    #     "AQT": 50,
    #     "CCV": 50,
    #     "CAV": 50,
    #     "COS": 50,
    #     "RGB": 50,
    #     "RIC": 50,
    #     "TSTD": 50,
    #     "TSIZE": 50,
    #     "CC": 50,
    #     "final_score" : 71 
    # }

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(port=7880)
# if __name__ == '__main__':
#     app.run(debug=True)