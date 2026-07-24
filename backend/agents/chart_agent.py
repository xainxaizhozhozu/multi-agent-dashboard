"""Chart Agent: 将 SQL 查询结果转换为 ECharts 图表配置，支持 line/bar/pie/combo"""

import json
import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ChartAgent(BaseAgent):

    SYSTEM_PROMPT = """你是数据可视化专家，将结构化数据转换为 ECharts option JSON。

输入：columns（列名）, data（行数据）, chart_type, chart_title

输出 ECharts option，必须包含：title, tooltip, xAxis/yAxis(bar/line), series, color

line: xAxis.data=日期, series.type=line, 可加 smooth
bar: xAxis.data=类别, series.type=bar, 建议加 label show
pie: 无 xAxis/yAxis, series.data=[{name,value}], label formatter '{b}: {c} ({d}%)'
combo: series.type=custom + stat_cards + summary_text

返回纯 JSON，不要 Markdown 标记。"""

    async def process(self, input_data: dict) -> dict:
        chart_type = input_data.get("chart_type", "bar")
        chart_title = input_data.get("chart_title", "数据分析图表")
        columns = input_data.get("columns", [])
        rows = input_data.get("data", [])

        if not rows:
            return {"error": "查询结果为空，请尝试其他维度", "needs_retry": True, "chart_config": None}

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({
                "columns": columns, "data": rows,
                "chart_type": chart_type, "chart_title": chart_title,
            }, ensure_ascii=False)},
        ]

        result = await self._call_llm(messages)

        try:
            result = result.strip()
            if result.startswith("```"):
                result = "\n".join(l for l in result.split("\n") if not l.strip().startswith("```"))
            chart_config = json.loads(result)
        except json.JSONDecodeError as e:
            logger.warning(f"Chart JSON parse failed, using fallback: {e}")
            chart_config = self._generate_fallback_chart(columns, rows, chart_type, chart_title)

        return {
            "chart_config": chart_config,
            "chart_type": chart_type,
            "chart_title": chart_title,
            "raw_data": rows,
            "columns": columns,
        }

    def _generate_fallback_chart(self, columns, rows, chart_type, title):
        """LLM 不可用时的降级方案"""
        if not columns or not rows:
            return {}

        x_data = [str(row[0]) for row in rows]
        y_data = []
        for row in rows:
            val = row[1] if len(row) > 1 else row[0]
            try:
                y_data.append(float(val))
            except (ValueError, TypeError):
                y_data.append(0)

        if chart_type == "line":
            return {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": x_data},
                "yAxis": {"type": "value"},
                "series": [{"type": "line", "data": y_data, "smooth": True}],
                "color": ["#5470c6"],
            }
        elif chart_type == "pie":
            pie_data = [{"name": str(r[0]), "value": r[1] if len(r) > 1 else r[0]} for r in rows]
            return {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "item"},
                "series": [{"type": "pie", "radius": ["40%", "70%"], "data": pie_data}],
                "color": ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de"],
            }
        else:
            return {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": x_data},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": y_data}],
                "color": ["#5470c6"],
            }
