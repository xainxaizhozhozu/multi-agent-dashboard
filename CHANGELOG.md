# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
