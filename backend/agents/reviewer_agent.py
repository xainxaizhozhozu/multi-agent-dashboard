"""Review Agent: SQL 安全检查 + 图表配置完整性校验，决定是否通过"""

import logging
logger = logging.getLogger(__name__)


class ReviewerAgent:

    def validate_sql(self, sql: str) -> dict:
        issues = []
        cleaned = sql.strip().upper()

        dangerous = ["DROP", "DELETE FROM", "UPDATE", "INSERT INTO",
                     "ALTER TABLE", "TRUNCATE", "EXEC ", "xp_"]
        for keyword in dangerous:
            if keyword in cleaned:
                issues.append(f"安全违规：包含 {keyword}")

        if not cleaned.startswith("SELECT"):
            issues.append("SQL 应以 SELECT 开头")

        if "SELECT *" in cleaned:
            issues.append("建议指定具体字段而非 SELECT *")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "severity": "high" if any("安全" in i for i in issues) else "low",
        }

    def validate_chart(self, chart_config: dict) -> dict:
        issues = []
        if not chart_config:
            return {"passed": False, "issues": ["图表配置为空"]}

        if "series" not in chart_config:
            issues.append("缺少 series 字段")
        if "title" not in chart_config:
            issues.append("缺少 title 字段")

        return {"passed": len(issues) == 0, "issues": issues}

    async def process(self, input_data: dict) -> dict:
        sql = input_data.get("sql", "")
        chart_config = input_data.get("chart_config")

        sql_check = self.validate_sql(sql) if sql else {"passed": True, "issues": []}
        chart_check = self.validate_chart(chart_config)

        all_issues = sql_check["issues"] + chart_check["issues"]
        is_passed = sql_check["passed"] and chart_check["passed"]

        result = {
            "review_passed": is_passed,
            "sql_validation": sql_check,
            "chart_validation": chart_check,
        }

        if is_passed:
            logger.debug("[Review] all checks passed")
            result["message"] = "校验通过"
        else:
            logger.warning(f"[Review] {len(all_issues)} issues found")
            result["issues"] = all_issues
            high_severity = [i for i in all_issues if "安全" in i or "为空" in i]
            result["can_partial_pass"] = not bool(high_severity)
            if not high_severity:
                result["message"] = "存在低级别问题但不影响基本功能"

        return result
