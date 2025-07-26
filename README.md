# ModelsEvaluator 
深度学习模型安全评测平台

## 系统架构
- 系统使用python Flask框架构建，提供用户数据上传和评测结果显示
- 使用两台服务器，一台作为访问机，具有公网IP，提供对外的访问服务；另一台服务器作为评测机，负责加载模型并执行评测

## 启动方法
1. 在访问机开启一个终端，建立ssh本地端口转发，使用调用评测机的LLM服务
```bash
ssh -L 6000:127.0.0.1:5000 ai-defender@47.117.171.217 -p 9530
```
输入密码后登录评测机，然后在本终端中远程启动LLM服务，看到5000端口上有服务开启即为成功
```bash
conda activate baichuan2
cd model_service
python service.py
```
2. 在访问机另开启一个终端，启动评测系统
```bash
conda activate Defender
cd Models-Evaluator
python app.py
```
## To Do
- [ ] 修复页面中存在的bug，使评测功能正常运转
- [ ] 重构页面，使页面更加美观，包括顶部菜单、页面背景和项目框等
