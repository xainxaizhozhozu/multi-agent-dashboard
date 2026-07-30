# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please do NOT open a public GitHub issue.

Instead, email us at **ck20060210@qq.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge receipt within 48 hours and provide a detailed response within 7 days.

## Security Measures

- SQL queries are executed in **read-only mode** at the SQLite engine level
- All LLM-generated SQL is validated with regex word-boundary matching before execution
- Multi-statement SQL (semicolons) is blocked to prevent injection chains
- API inputs are validated with length limits
- Internal error details are not exposed to clients
- Environment variables (.env) are excluded from version control

## Best Practices for Deployment

- Set `USE_MOCK_MODE=false` and provide a real API key via `OPENAI_API_KEY` environment variable
- Never commit `.env` files or API keys to version control
- Use HTTPS in production (configure via reverse proxy like nginx or Traefik)
- Set strong CORS origins instead of `*` in production
- Run behind a reverse proxy with rate limiting
