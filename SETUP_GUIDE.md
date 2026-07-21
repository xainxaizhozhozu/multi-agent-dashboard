"""多智能体数据分析系统 — 完整搭建与运行指南"""

# ════════════════════════════════════════
# 项目一：Multi-Agent 智能数据分析看板
# ════════════════════════════════════════

本项目是一个基于多智能体协作的企业级数据分析平台。用户通过自然语言提问，系统自动调用四个 AI Agent（Router → SQL → Chart → Reviewer）完成从数据查询到可视化展示的全流程。

## 环境要求
- Python 3.10+ （你已有 3.13 ✅）
- Node.js 18+ （需要安装！详见下方）
- Git （你已有 ✅）

## 第一步：安装 Node.js

由于你的电脑上还没有 Node.js，请先安装：

1. 打开 https://nodejs.org/zh-cn/download/prebuilt-installer
2. 选择 **Windows 安装包 (.msi)** ，版本选 **LTS (Long Term Support)** 
3. 双击安装包，一路"下一步"即可
4. ⚠️ 安装时确保勾选了 "Add to PATH"
5. 关闭当前所有终端窗口，重新打开 PowerShell

验证安装：
```powershell
node --version    # 应该显示 v20.x.x
npm --version     # 应该显示 10.x.x
```

## 第二步：启动后端服务

打开 PowerShell，依次执行：

```powershell
cd C:\Users\Administrator\.qoderworkcn\workspace\mrsnqfo0v2s063de\outputs\project-1-multi-agent-dashboard\backend

# 创建虚拟环境（只需执行一次）
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 如果上面报错，说 "无法加载文件...因为在此系统上禁止运行脚本"
# 则以管理员身份打开 PowerShell，执行：
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# 然后重新输入上面的激活命令

# 安装 Python 依赖（首次需要下载一些包，等几十秒）
pip install -r requirements.txt

# 启动后端服务
python main.py
```

看到以下输出说明成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

此时可以访问 http://localhost:8000/docs 查看 API 文档。

**⚠️ 如果安装失败：**
可以直接手动装最核心的包：
```powershell
pip install fastapi uvicorn pydantic python-dotenv sqlite-utils
```
把 requirements.txt 中的 crewai / langchain 去掉（Mock 模式不需要这些）。

## 第三步：启动前端服务

开一个新的 PowerShell 窗口（不要关掉后端的）：

```powershell
cd C:\Users\Administrator\.qoderworkcn\workspace\mrsnqfo0v2s063de\outputs\project-1-multi-agent-dashboard\frontend

# 安装前端依赖（首次较慢，等 1-2 分钟）
npm install

# 启动开发服务器
npm run dev
```

看到类似输出说明成功：
```
  VITE v6.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

点击 http://localhost:5173/ 即可在浏览器中打开应用！

## 第四步：测试完整流程

1. 打开 http://localhost:5173/
2. 你会看到仪表盘界面和底部的聊天框
3. 点击预设的问题按钮或自行输入，例如：
   - "华东区上个月的销售额是多少？"
   - "各产品类别的销售占比情况"
   - "最近三个月的收入趋势怎么样"
4. 四个 Agent 会依次工作并返回图表结果 🎉

## 切换到真实 LLM 模式（可选）

如果你想使用真实的 GPT 模型：

1. 进入 `backend` 目录
2. 复制环境变量文件：
   ```powershell
   copy .env.example .env
   ```
3. 编辑 `.env`：
   ```
   USE_MOCK_MODE=false
   OPENAI_API_KEY=sk-your-real-key-here
   OPENAI_BASE_URL=https://api.openai.com/v1
   MODEL_NAME=gpt-4o-mini
   ```
4. 重启后端服务

> 💡 推荐替代方案（国内更友好）：使用阿里云通义千问
> ```
> USE_MOCK_MODE=false
> OPENAI_API_KEY=your-dashscope-key
> OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
> MODEL_NAME=qwen-plus
> ```
> DashScope 注册地址：https://dashscope.console.aliyun.com/ （新用户送额度）

---

## 项目结构速览

```
project-1-multi-agent-dashboard/
├── backend/                          ← Python 后端
│   ├── main.py                       ← FastAPI 入口
│   ├── schemas/
│   │   └── database.py               ← 数据库建表 + Mock 数据
│   ├── services/
│   │   ├── llm_service.py            ← LLM 接口封装 (Mock/OpenAI)
│   │   ├── query_executor.py         ← SQL 安全执行器
│   │   └── orchestrator.py           ← 四 Agent 编排器 ⭐核心
│   ├── agents/                       ← 四个智能体
│   │   ├── router_agent.py           ← Router — 意图识别
│   │   ├── sql_agent.py              ← SQL — 数据查询
│   │   ├── chart_agent.py            ← Chart — 可视化生成
│   │   └── reviewer_agent.py         ← Review — 质量审查
│   └── routers/                      ← API 路由
│       ├── dashboard.py              ← 看板统计接口
│       └── agent.py                  ← Agent 对话接口
├── frontend/                         ← React 前端
│   ├── src/
│   │   ├── App.jsx                   ← 主布局组件
│   │   ├── api.js                    ← API 请求封装
│   │   └── index.css                 ← Tailwind 样式
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 面试时可以讲的要点

### 架构设计
- 采用 Pipeline 模式组织多 Agent 协作流
- Review Agent 引入 Reflection 机制，失败时可打回上游重做
- 统一 LLM 接口层，支持 Mock/OpenAI/通义千问无缝切换

### 技术亮点
1. **SQL 安全防护** — 只允许 SELECT，拦截危险关键词
2. **降级策略** — Chart Agent 内置 fallback 渲染逻辑
3. **端到端链路** — 自然语言→SQL→数据→ECharts配置，全自动化

### 可扩展方向
- 新增 PDF 导出 Agent
- 接入 PostgreSQL 替代 SQLite
- 添加用户认证和权限管理
- 支持多个图表的组合 Panel
