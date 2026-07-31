# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.4.0] - 2026-08-01

### Added
- **Frontend component splitting**: Extracted 5 reusable components from monolithic App.jsx (433→87 lines): StatCard, AgentChart, AgentResponse, DashboardCharts, ChatPanel
- **Pipeline type contracts**: Added `services/pipeline_types.py` with TypedDict definitions (RouterOutput, SQLAgentOutput, ChartAgentOutput, ReviewerOutput, PipelineResult) documenting inter-agent data flow
- **Component tests**: Added 19 frontend tests for StatCard (4), ChatPanel (6), AgentResponse (9) — total frontend tests now 40
- **ResizeObserver mock**: Added to test setup for Recharts compatibility in jsdom environment

### Changed
- **Schema separation**: Created `models/` package (dataclass: Sales, Employee, Product) and `schemas/` package (Pydantic: ChatRequest, DashboardStats, MonthlyTrend, etc.)
- **Centralized config**: `services/llm_service.py` now uses `core.config.Settings` instead of `os.getenv()`
- **Database split**: `schema/database.py` simplified to connection + table creation; seed data extracted to `schema/seed_data.py`
- **Pydantic validation**: `routers/agent.py` now uses `ChatRequest` model (422 for invalid input, whitespace rejection)
- **Package structure**: Added `__init__.py` to routers/, services/, schema/ for explicit package declarations

### Fixed
- **Dashboard field name**: `stats.month_revenue` → `stats.this_month_revenue` (matching backend response)
- **Connection leak**: `routers/dashboard.py` `get_db()` converted to FastAPI dependency with yield/finally
- **Bare except**: `agents/sql_agent.py` narrowed to `except (json.JSONDecodeError, KeyError)` with regex fallback
- **Lazy init**: `routers/agent.py` orchestrator uses deferred singleton pattern
- **Query length**: Added 500-char max validation on agent chat input
- **Mom calculation**: Fixed division-by-zero when last_month_sales is 0

### Infrastructure
- Docker (backend + frontend + nginx), docker-compose.yml
- GitHub Actions CI/CD pipeline
- Pre-commit hooks (ruff, black, mypy)
- pytest (66 backend tests) + Vitest + React Testing Library (40 frontend tests)
- SECURITY.md, CONTRIBUTING.md, issue templates
- English README summary, .env.example

## [v1.2.0] - 2026-07-30

### Security
- SQL queries now run in read-only mode to prevent accidental data modification
- Added comprehensive input validation on all API endpoints
- Sanitized error messages to avoid leaking internal implementation details

## [v1.1.0] - 2026-07-30

### Added
- MIT License for open-source distribution

### Changed
- Cleaned up and consolidated project dependencies

## [v1.0.0] - 2026-07-28

### Added
- Initial release of the Multi-Agent Data Analytics Dashboard
- Natural language to SQL conversion powered by LLM agents
- Interactive chart rendering and data visualization
- FastAPI backend with SQLite storage
- React + Vite frontend with Tailwind CSS
