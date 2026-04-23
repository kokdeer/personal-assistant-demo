# tools.py
import datetime
import json
from typing import List, Optional
from dateutil import parser
import dateparser
import requests
from langchain.tools import tool

# ---------- 提醒存储（内存）----------
_reminders: List[dict] = []

@tool
def get_current_time() -> str:
    """获取当前日期和时间，格式为 YYYY-MM-DD HH:MM:SS 星期几。"""
    now = datetime.datetime.now()
    weekday = ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
    return f"现在是 {now.strftime('%Y-%m-%d %H:%M:%S')} 星期{weekday}"

@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气情况。参数 city 为城市名称（中文或英文）。"""
    # 模拟数据，可替换为真实 API（如高德、wttr.in）
    mock_weather = {
        "北京": "晴，温度 22°C，湿度 45%，北风 3级",
        "上海": "多云，温度 25°C，湿度 60%，东南风 2级",
        "深圳": "阵雨，温度 28°C，湿度 80%，南风 4级",
        "default": "晴间多云，温度 20°C，湿度 50%"
    }
    return mock_weather.get(city, mock_weather["default"]) + f" （{city}）"

@tool
def search_news(query: str, limit: int = 3) -> str:
    """搜索最新新闻，参数 query 为搜索关键词，limit 为返回条数（默认3）。"""
    # 模拟新闻数据
    mock_news = [
        {"title": f"{query} 取得新突破", "source": "科技日报"},
        {"title": f"关于 {query} 的最新政策解读", "source": "新华网"},
        {"title": f"{query} 市场分析报告发布", "source": "财经周刊"},
        {"title": f"专家谈 {query} 的未来趋势", "source": "凤凰网"}
    ]
    import random
    selected = random.sample(mock_news, min(limit, len(mock_news)))
    lines = [f"• {item['title']} —— {item['source']}" for item in selected]
    return "最新新闻：\n" + "\n".join(lines)

@tool
def calculator(expression: str) -> str:
    """执行数学计算，支持加减乘除、括号、幂运算等。参数 expression 为数学表达式字符串。"""
    # 安全限制：只允许数字、运算符、空格和括号
    allowed = set("0123456789+-*/().^ ")
    if not all(c in allowed for c in expression):
        return "错误：表达式包含非法字符，仅支持基本数学运算。"
    # 替换 ^ 为 ** 以支持幂运算
    expr = expression.replace("^", "**")
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算出错：{str(e)}"

@tool
def add_reminder(content: str, remind_time: str) -> str:
    """添加一条提醒。参数 content 为提醒内容，remind_time 为提醒时间（自然语言，如'明天下午3点'或'2025-06-01 10:00'）。"""
    # 解析时间
    parsed_time = dateparser.parse(remind_time, languages=['zh', 'en'])
    if not parsed_time:
        return f"无法解析时间 '{remind_time}'，请使用更明确的表述。"
    reminder = {
        "content": content,
        "time": parsed_time.strftime("%Y-%m-%d %H:%M"),
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    _reminders.append(reminder)
    return f"已添加提醒：{content}，时间：{reminder['time']}"

@tool
def list_reminders() -> str:
    """列出所有已设置的提醒。"""
    if not _reminders:
        return "当前没有任何提醒。"
    lines = ["当前提醒列表："]
    for i, r in enumerate(_reminders, 1):
        lines.append(f"{i}. {r['content']} @ {r['time']}")
    return "\n".join(lines)

# 工具列表导出
ALL_TOOLS = [get_current_time, get_weather, search_news, calculator, add_reminder, list_reminders]