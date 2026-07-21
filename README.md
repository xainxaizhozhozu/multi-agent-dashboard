# 项目一：Multi-Agent 智能数据分析与自动化报表系统

## 技术栈
- **Agent 框架**: CrewAI（多智能体编排）
- **LLM**: OpenAI GPT-4o-mini / 阿里云通义千问
- **后端**: FastAPI + SQLite
- **前端**: React + Vite + TailwindCSS + Recharts
- **可视化**: Apache ECharts / Recharts

## 快速开始

### 后端
```bash
cd backend
virtualenv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python main.py               # 访问 http://localhost:8000/docs
```

### 前端
```bash
cd frontend
npm install
npm run dev                  # 访问 http://localhost:5173
```

## 系统架构

```
用户自然语言输入
       │
       ▼
┌──────────────┐
│  Router Agent│ ← 解析意图，拆解任务流
└──────┬───────┘
       │
       ├──► SQL Agent ──► 生成并执行 SQL ──► 数据结果
       │
       ├──► Chart Agent ──► 选择图表类型 ──► ECharts 配置
       │
       └──► Review Agent ──► 校验SQL和Chart ──► 通过/打回
                                    │
                              不通过则回到对应 Agent
                                    │
                                    ▼
                             返回前端渲染看板
```

## 功能截图
（开发完成后在此处添加截图）

## 核心亮点
1. **多智能体协作** — 四个 Agent 各司其职，解耦设计易于扩展
2. **Reflection 机制** — Review Agent 对 SQL 和图表配置进行二次校验
3. **端到端链路** — 用户说一句话 → 拿到一个完整的动态仪表盘
