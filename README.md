# 智能数据分析看板（Multi-Agent 协作系统）

基于多 Agent 协作的自然语言数据分析平台。用户用中文提问，系统自动完成意图解析、SQL 生成、图表推荐与质量校验，实时渲染专业级数据看板。

## 功能亮点

- 自然语言提问，自动生成 SQL 并执行查询
- 4-Agent 流水线：Router → SQL → Chart → Review，含自动校验与重试
- 支持折线图、柱状图、饼图等多种图表动态渲染
- 覆盖 7 类查询场景：趋势分析、TOP 排名、占比分布、地区对比、薪资统计等
- Mock / 真实大模型双模式热切换，开发零成本调试
- 预设看板 + 自由问答两种交互模式

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python / FastAPI / SQLite / LangChain |
| 前端 | React / Vite / TailwindCSS / Recharts |
| AI | 大模型 API（OpenAI 兼容协议） |
| 部署 | 本地开发，前后端分离 |

## 系统架构

```
用户提问
  ↓
Router Agent（意图识别）
  ↓
SQL Agent（调用大模型生成 SQL）
  ↓
Query Executor（执行 SQL，返回数据）
  ↓
Chart Agent（决定图表类型与配置）
  ↓
Review Agent（校验结果，异常则重试）
  ↓
前端渲染图表 + 数据表格
```

## 快速启动

### 后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

配置 `.env`：

```
USE_MOCK_MODE=true           # true=模拟模式，false=调用真实大模型
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://token.sensenova.cn/v1
MODEL_NAME=deepseek-v4-flash
```

启动：

```bash
set PYTHONPATH=%cd%          # Windows CMD
uvicorn main:app --reload    # 访问 http://localhost:8000
```

### 前端

```bash
cd frontend
npm install
npm run dev                  # 访问 http://localhost:5173
```

## 项目结构

```
multi-agent-dashboard/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── agents/              # 4 个 Agent 实现
│   │   ├── router_agent.py
│   │   ├── sql_agent.py
│   │   ├── chart_agent.py
│   │   └── review_agent.py
│   ├── services/
│   │   ├── llm_service.py   # 大模型调用（Mock/真实）
│   │   ├── orchestrator.py  # Agent 编排调度
│   │   └── query_executor.py
│   ├── routers/             # API 路由
│   ├── schema/              # 数据库初始化与种子数据
│   └── data/                # SQLite 数据库文件
├── frontend/
│   └── src/
│       ├── App.jsx          # 主页面（看板 + AI 对话）
│       └── api.js           # 接口封装
└── README.md
```

## 示例问答

| 用户提问 | 系统响应 |
|---------|---------|
| 各地区销售额对比 | 柱状图 + 数据表 |
| 月度销售趋势 | 折线图 |
| 产品类别销售占比 | 饼图 |
| 各部门平均薪资 | 柱状图 |
| 客户类型消费占比 | 饼图 |

## 作者

陈科 | 独立开发 |
