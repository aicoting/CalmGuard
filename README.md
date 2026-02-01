<p align="center">
  <h2 align="center">🎯 CalmGuard</h2>
  <p align="center">
    面向具体场景的AI落地实战项目！
    <br/>
    <br/>
    <a href="https://aicoting.cn/"><strong>» 查看项目手册 »</strong></a>
    <br/>
  </p>
</p>

<p align="center">
  <a href="https://github.com/aicoting/CalmGuard/stargazers">
    <img src="https://img.shields.io/github/stars/aicoting/CalmGuard?color=F8B195&logo=github&style=for-the-badge" alt="Github stars">
  </a>
  <a href="https://pypi.org/project/CalmGuard/">
    <img src="https://img.shields.io/pypi/v/CalmGuard?color=F67280&logo=pypi&logoColor=white&style=for-the-badge" alt="PyPI">
  </a>
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/aicoting/CalmGuard?color=C06C84&style=for-the-badge" alt="License">
  </a>
</p>

<p align="center">
  <a href="https://www.zhihu.com/people/wu-wang-wo-24-38"><img src="https://img.shields.io/badge/ZhiHu-知乎-8c36db" /></a>&emsp;
  <a href="https://space.bilibili.com/3546955336649590?spm_id_from=333.1387.0.0"><img src="https://img.shields.io/badge/Bilibili-B站-ff69b4" /></a>&emsp;
  <a href="https://juejin.cn/user/933911964427818"><img src="https://img.shields.io/badge/Juejin-掘金-FF6600?style=flat&logo=juejin&logoColor=white" /></a>&emsp;
  <a href="https://blog.csdn.net/weixin_53004531?spm=1000.2115.3001.5343"><img src="https://img.shields.io/badge/CSDN-博客-0066B3?style=flat&logo=csdn&logoColor=white" /></a>&emsp;
  <a href="https://www.youtube.com/channel/UCZFnqiae-NLdu-4uJJZscQg"><img src="https://img.shields.io/badge/YouTube-油管-c32136" /></a>&emsp;
  <!-- visitor -->
  <img src="https://komarev.com/ghpvc/?username=zhangting-hit&label=Views&color=orange&style=flat" alt="访问量统计" />&emsp;
  <!-- wakatime -->    
  <a href="https://wakatime.com/@zhangting-hit"><img src="https://wakatime.com/badge/user/42d0678c-368b-448b-9a77-5d21c5b55352.svg" /></a>
</p>

**CalmGuard** 是一款面向企业级的 AI 对话系统，专为银行客户服务设计。它擅长处理高摩擦场景，如客户投诉、账户风险事件及情绪升级。与通用聊天机器人不同，CalmGuard 采用多阶段流水线，对用户意图、情绪和风险进行评估，然后生成合规、富有同理心且策略性强的回应。

<div align="center">

![CalmGuard Web 界面](./imgs/CalmGuard%20web界面.png)

</div>

---

## 🚀 核心功能

| 功能模块 | 描述 |
|----------|------|
| **意图识别** | 精准分类用户意图（投诉、咨询、威胁、风险事件） |
| **情绪与风险评估** | 实时评分用户情绪（0-3）并识别高风险标签（法律威胁、媒体曝光、监管投诉） |
| **动态策略路由** | 自动选择最佳应对策略：<br>• **先安抚**：情绪激动但低风险<br>• **先解释**：处理标准咨询<br>• **升级处理**：高敌意或已确认风险事件<br>• **风险拒绝**：礼貌拒绝不合规要求 |
| **合规响应生成** | 生成银行级安全回应，避免法律责任，同时缓解紧张情绪 |
| **透明调试** | 实时可视化 AI 决策流程（意图 -> 情绪 -> 策略） |

---

## 🛠 技术栈

* **前端**：React 18 (TypeScript)、Vite、Ant Design  
* **后端**：Python 3.9+、FastAPI、Pydantic  
* **AI 核心**：OpenAI GPT-3.5/4（兼容任何 OpenAI API）、Prompt 工程  
* **架构模式**：模块化流水线

---

## 😺 大模型 API 选择

CalmGuard 支持多种大模型调用方式，可按需选择：

1. **本地部署**  
   - 使用 vLLM / Ollama / Xinference 等框架，私有化运行开源模型（如 Qwen、ChatGLM、Baichuan）  
   - 零外泄风险  

2. **OpenAI**  
   - 直接调用官方 GPT-3.5 / GPT-4 接口  
   - 无需额外适配  

3. **阿里云（通义千问）**  
   - 通过 DashScope API 调用通义千问系列模型  
   - 国内网络友好、按量计费  

> 只需在 `backend/.env` 中配置对应 `BASE_URL`、`API_KEY` 及 `MODEL_ID`，系统会自动切换后端渠道。

---

## 📂 项目结构

```
CalmGuard/
├── backend/               # FastAPI Backend
│   ├── app/
│   │   ├── main.py        # API Entry Point
│   │   ├── services.py    # LLM Pipeline Logic
│   │   ├── models.py      # Data Models (Pydantic)
│   │   └── prompts.py     # Prompt Loader
│   └── requirements.txt   # Python Dependencies
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── App.tsx        # Main Chat Interface
│   │   └── ...
│   └── package.json
├── prompts/               # System Prompts (Markdown)
│   ├── system_role.md
│   ├── intent_detection.md
│   ├── emotion_risk.md
│   └── ...
└── README.md
```


## ⚡ 快速启动

### 前置条件
* Node.js & npm  
* Python 3.8+  
* OpenAI API Key（演示模式可选）

### 1. 后端配置

```bash
cd backend
# 创建虚拟环境（可选）
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置 API（可选）
# 复制 .env.example 为 .env，填入 HF_TOKEN 以使用 Hugging Face 推理 API
# 或设置 OPENAI_API_KEY 使用 OpenAI。若均未设置，则运行 MOCK 演示模式。

# 启动服务
uvicorn app.main:app --reload
```

### 2. 前端配置

```bash
cd frontend
npm install
npm run dev
```

Web UI 将启动在 `http://localhost:5173`.

## 🧠 Prompt 工程策略
本项目采用 Chain-of-Thought 与 流水线 方法。不是单一的“万能 Prompt”，而是拆分任务：

1. **输入** -> **意图分类器（JSON）**
2. **输入** -> **情绪/风险评分（JSON）**
3. **意图 + 情绪** -> **策略路由器（JSON）**
4. **策略 + 输入** -> **回应生成器（文本）**

这样相比单次生成，可获得更高的控制力、可审计性和合规性。

## 🔧 故障排查

### LLM Error: Not Found
若出现 `LLM Error (Intent/Emotion/Strategy/Response): Not Found`，通常是 Hugging Face API 配置有误。请确保：
1. **base URL** 为 `https://router.huggingface.co/v1`（不要包含模型路径）
2. **模型 ID** 为官方支持的格式，如 `Qwen/Qwen2.5-7B-Instruct`
3. **HF_TOKEN** 在 `backend/.env` 中正确配置，且具有 "Inference Providers" 权限

### Mock 模式
若未设置 `HF_TOKEN` 或 `OPENAI_API_KEY`，系统自动切换为 Mock 模式，使用规则引擎模拟 AI 响应，便于本地演示。

## ⚠️ 免责声明

本项目仅用于教育和作品展示目的。虽然设计中考虑了合规性，但真实银行系统需要严格的法律审核和本地部署。
