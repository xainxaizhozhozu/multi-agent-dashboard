"""
Chart Agent（可视化智能体）

职责：根据数据特征和 Router 的推荐，生成 ECharts 图表配置。

工作流程：
1. 接收 SQL Agent 返回的数据结果 + Router 推荐的图表类型
2. 分析数据结构（几列？每列是什么类型？）
3. 生成对应的 ECharts option 配置对象
4. 处理边界情况（空数据、单条数据等）

### ECharts 图表类型映射：
- line → 折线图（适合趋势展示）
- bar → 柱状图（适合对比展示）
- pie → 饼图（适合占比展示）
- combo → 组合面板（多个统计卡片）

### ECharts JavaScript 库引入方式（前端实现）：
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
"""

import json
from datetime import datetime
from services.llm_service import LLMService
from agents.base_agent import BaseAgent


class ChartAgent(BaseAgent):
    """Chart Agent — 数据的视觉翻译官"""

    SYSTEM_PROMPT = """你是一个数据可视化专家。你的任务是将结构化数据转换为专业的 ECharts 图表配置。

### 输入数据格式：
{
    "columns": ["region", "total_amount"],   // 列名
    "data": [                                  // 行数据
        ["华东", 1250000],
        ["华南", 980000],
        ["华北", 760000]
    ],
    "chart_type": "bar",                     // 图表类型
    "chart_title": "各地区销售总额对比"       // 标题
}

### 输出要求：
返回一个 ECharts option JSON 对象，必须包含以下字段：

{
    "title": { "text": "图表标题" },
    "tooltip": { "trigger": "axis|item" },     // axis=柱/线, item=饼图节点
    "xAxis": { ... }                            // 仅 bar/line 需要
    "yAxis": { ... },                           // 仅 bar/line 需要
    "series": [                                  // 数据系列
        {
            "name": "指标名称",
            "type": "bar|line|pie",
            "data": [...]                        // 具体数据
        }
    ],
    "color": ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de"]  // 配色
}

### 各图表类型的具体要求：

**折线图 (line) — 用于时间序列/趋势：**
- xAxis.type = 'category'
- xAxis.data = 日期数组
- series.type = 'line'
- series.data = 数值数组
- 可以加 smooth: true 让线条更平滑

**柱状图 (bar) — 用于分类对比：**
- xAxis.type = 'category'  
- xAxis.data = 类别名称数组
- series.type = 'bar'
- series.data = 数值数组
- 建议加 label: { show: true } 显示数值

**饼图 (pie) — 用于占比分析：**
- 不需要 xAxis/yAxis
- series.type = 'pie'
- series.data = [{ name: 'xx', value: xx }, ...]
- 加 label: { formatter: '{b}: {c} ({d}%)' }

**组合面板 (combo) — 用于统计概览：**
series.type = 'custom' 且同时提供:
- stat_cards: [{"label": "总销售额", "value": 1250000}, ...]
- summary_text: "一段总结性描述"
"""

    async def process(self, input_data: dict) -> dict:
        data_result = input_data
        chart_type = data_result.get("chart_type", "bar")
        chart_title = data_result.get("chart_title", "数据分析图表")
        columns = data_result.get("columns", [])
        rows = data_result.get("data", [])

        # ── 如果数据为空 ────────────────────────────────
        if not rows or len(rows) == 0:
            return {
                "error": "查询结果为空，请尝试其他维度",
                "needs_retry": True,
                "chart_config": None,
            }

        # ── 生成 ECharts 配置 ──────────────────────────
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({
                "columns": columns,
                "data": rows,
                "chart_type": chart_type,
                "chart_title": chart_title,
            }, ensure_ascii=False)},
        ]

        result = await self._call_llm(messages)

        try:
            # 清理可能的 Markdown 标记
            result = result.strip()
            if result.startswith("```"):
                result_lines = [l for l in result.split("\n") if not l.strip().startswith("```")]
                result = "\n".join(result_lines)

            chart_config = json.loads(result)
        except json.JSONDecodeError as e:
            print(f"⚠ Chart Agent JSON 解析失败: {e}")
            # 降级方案：使用默认配置
            chart_config = self._generate_fallback_chart(columns, rows, chart_type, chart_title)

        return {
            "chart_config": chart_config,
            "chart_type": chart_type,
            "chart_title": chart_title,
            "raw_data": rows,
            "columns": columns,
        }

    def _generate_fallback_chart(self, columns, rows, chart_type, title):
        """
        降级方案：当 LLM 不可用时自动生成基础 ECharts 配置。
        
        这是 Mock 模式的核心——即使不调用 LLM，系统也能生成可用图表。
        """
        if not columns or not rows:
            return {}

        first_col = columns[0]
        second_col = columns[1] if len(columns) > 1 else columns[0]

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
                "series": [{
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "data": pie_data,
                }],
                "color": ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de"],
            }
        else:  # bar (default)
            return {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": x_data},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": y_data}],
                "color": ["#5470c6"],
            }
