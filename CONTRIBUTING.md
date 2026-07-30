# 贡献指南

感谢你对本项目的关注！以下是参与贡献的完整流程。

## 开发环境搭建

### 前置要求

- Python 3.12+
- Node.js 20+
- Git

### 后端环境

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 前端环境

```bash
cd frontend
npm install
```

## 本地运行

### 启动后端

```bash
cd backend
uvicorn main:app --reload --port 8000
```

后端服务将运行在 http://localhost:8000，API 文档位于 http://localhost:8000/docs。

### 启动前端

```bash
cd frontend
npm run dev
```

前端开发服务器将运行在 http://localhost:5173。

### 使用 Docker Compose 一键启动

```bash
docker compose up --build
```

前端访问 http://localhost:3000，后端访问 http://localhost:8000。

## 代码风格

本项目使用 [ruff](https://github.com/astral-sh/ruff) 作为 Python 代码的 linter 和格式化工具。

```bash
# 安装 ruff
pip install ruff

# 检查代码
ruff check backend/

# 自动修复
ruff check --fix backend/

# 格式化代码
ruff format backend/
```

建议安装 pre-commit 钩子以在提交前自动执行检查：

```bash
pip install pre-commit
pre-commit install
```

## 提交 PR

1. Fork 本仓库并克隆到本地。
2. 创建功能分支：`git checkout -b feature/your-feature-name`。
3. 完成开发并确保通过所有 lint 检查。
4. 提交代码：`git commit -m "feat: 简要描述你的改动"`。
5. 推送到你的 Fork：`git push origin feature/your-feature-name`。
6. 在 GitHub 上创建 Pull Request，目标分支为 `main`。

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复缺陷
- `docs:` 文档更新
- `refactor:` 代码重构
- `chore:` 构建或工具链变动

## 注意事项

- 提交前请确保 CI 检查能够通过。
- 不要在代码中硬编码密钥或敏感信息。
- 如有重大功能变更，请先在 Issue 中讨论方案。
