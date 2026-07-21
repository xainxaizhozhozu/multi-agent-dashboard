"""
Review Agent（审计/反思智能体）

职责：在最终输出给用户之前，对 SQL 和图表配置进行质量检查。

工作流程：
1. 接收 SQL Agent 的结果 + Chart Agent 的输出
2. 执行多维度校验：
   - SQL: 语法正确性、安全性、性能
   - Chart: 配置完整性、数据匹配度
3. 决定：通过 → 返回给前端 / 不通过 → 打回重做

### Reflection 机制的意义：
这是 Multi-Agent 系统的核心亮点之一。
单 Agent 系统一旦出错就没办法了，但多 Agent 系统中，
Review Agent 可以发现问题并触发重新生成，显著提升成功率。
"""

import json
from services.llm_service import LLMService


class ReviewerAgent:
    """Review Agent — 最后的质量把关人"""

    # ── 规则式校验（不需要调用 LLM，速度快）───────────────
    def validate_sql(self, sql: str) -> dict:
        """
        对 SQL 语句进行静态检查
        
        返回: {"passed": bool, "issues": [...], "suggestions": [...]}
        """
        issues = []
        cleaned = sql.strip().upper()

        # 1. 安全检查
        dangerous = ["DROP", "DELETE FROM", "UPDATE", "INSERT INTO", "ALTER TABLE", 
                     "TRUNCATE", "EXEC ", "xp_"]
        for keyword in dangerous:
            if keyword in cleaned:
                issues.append(f"安全违规：包含敏感操作 {keyword}")

        # 2. 基本语法检查
        if not cleaned.startswith("SELECT"):
            issues.append("语法问题：SQL 应以 SELECT 开头")

        # 3. 性能建议
        if "SELECT *" in cleaned.upper():
            issues.append("性能建议：建议指定具体字段而非使用 *")

        # 4. GROUP BY 检查
        if ("GROUP BY" in cleaned or "SUM(" in cleaned or "COUNT(" in cleaned) \
           and "GROUP BY" not in cleaned:
            # 有聚合函数但没有 GROUP BY（可能是统计总数，不算错误）
            pass  # 这不一定有问题，不做为 issue

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "severity": "high" if any("安全" in i or "语法" in i for i in issues) else "low",
        }

    def validate_chart(self, chart_config: dict) -> dict:
        """
        对 ECharts 配置进行完整性检查
        
        返回: {"passed": bool, "issues": [...]}
        """
        issues = []

        if not chart_config:
            issues.append("图表配置为空")
            return {"passed": False, "issues": issues}

        # 必须有 series
        if "series" not in chart_config:
            issues.append("缺少必需的 'series' 字段")

        # 必须有 title
        if "title" not in chart_config:
            issues.append("缺少 'title' 字段")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
        }

    async def process(self, input_data: dict) -> dict:
        """
        综合校验 SQL 和图表配置
        
        参数:
            input_data 包含:
            - sql: SQL 语句
            - data: 查询结果
            - chart_config: ECharts 配置
        """
        sql = input_data.get("sql", "")
        chart_config = input_data.get("chart_config")

        # ── 执行校验 ───────────────────────────────────
        sql_check = self.validate_sql(sql) if sql else {"passed": True, "issues": []}
        chart_check = self.validate_chart(chart_config)

        # ── 汇总结果 ───────────────────────────────────
        all_issues = (
            [{"[SQL] " + i} for i in sql_check["issues"]] +
            [{"[Chart] " + i} for i in chart_check["issues"]]
        )

        is_passed = sql_check["passed"] and chart_check["passed"]

        result = {
            "review_passed": is_passed,
            "sql_validation": sql_check,
            "chart_validation": chart_check,
        }

        if is_passed:
            print(f"✅ Review Agent: 校验通过 ✓")
            result["message"] = "所有检查项均已通过，可以交付给用户"
        else:
            print(f"⚠️  Review Agent: 发现 {len(all_issues)} 个问题")
            result["issues"] = all_issues
            
            # 根据严重程度决定是否可以部分通过
            high_severity = [i for i in all_issues if "安全" in i or "语法" in i or "为空" in i]
            if high_severity:
                result["can_partial_pass"] = False
            else:
                result["can_partial_pass"] = True
                result["message"] = "存在低级别问题但不影响基本功能，可以选择性展示"

        return result
