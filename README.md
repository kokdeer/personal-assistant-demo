# 🤖 多功能个人助理 Agent

基于 LangChain + Streamlit 构建的智能对话助理，支持 ReAct 推理、多工具调用和对话记忆。

## ✨ 功能特性

- **自然语言交互**：通过聊天界面与 Agent 对话。
- **ReAct 推理**：Agent 自主思考、调用工具、观察结果，完成多步任务。
- **多工具集成**：
  - `get_current_time` – 获取当前日期时间
  - `get_weather` – 查询城市天气（模拟数据）
  - `search_news` – 搜索最新新闻（模拟数据）
  - `calculator` – 安全执行数学计算
  - `add_reminder` / `list_reminders` – 设置和查看提醒（内存存储）
- **混合记忆**：
  - **短期窗口**：保留最近 N 轮对话。
  - **向量检索**：使用 Chroma 向量数据库召回相似历史对话，增强上下文理解。
- **灵活模型配置**：支持 OpenAI、DeepSeek 等兼容接口的模型。

## 🛠️ 技术栈

- **核心框架**：LangChain (Agent + Tools)
- **界面**：Streamlit
- **模型接入**：langchain-openai
- **向量数据库**：ChromaDB
- **时间解析**：dateparser
- **语言**：Python 3.9+
