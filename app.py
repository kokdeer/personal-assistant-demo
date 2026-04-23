# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from tools import ALL_TOOLS
from memory_manager import HybridMemory

# ---------- 加载环境变量 ----------
load_dotenv()

# 后端固定配置（从 .env 读取）
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

# 如果未设置 API_KEY，启动时直接报错提示
if not API_KEY:
    st.error("❌ 未找到 API Key！请在项目根目录创建 .env 文件并设置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY。")
    st.stop()

# ---------- 页面配置 ----------
st.set_page_config(page_title="🧠 个人助理 Agent", page_icon="🤖")
st.title("🤖 多功能个人助理 Agent")
st.caption("自然语言交互 · 查天气 · 搜新闻 · 计算 · 提醒 · 对话记忆")

# ---------- 侧边栏 ----------
with st.sidebar:
    st.header("⚙️ 设置")
    temperature = st.slider("温度", 0.0, 1.0, 0.1)
    st.divider()
    if st.button("🧹 清空对话历史"):
        st.session_state.messages = []
        st.session_state.hybrid_memory.clear_window()
        st.rerun()
    st.caption(f"🔧 当前模型：{MODEL_NAME}")

# ---------- 初始化 Agent（缓存）----------
@st.cache_resource
def init_agent(_api_key: str, _base_url: str, _model: str, _temp: float):
    llm = ChatOpenAI(
        api_key=_api_key,
        base_url=_base_url if _base_url else None,
        model=_model,
        temperature=_temp,
        timeout=60
    )

    system_prompt = SystemMessage(content="""
你是一个智能个人助理，名字叫“小智”。你可以使用以下工具：
- get_current_time: 获取当前时间
- get_weather: 查询城市天气
- search_news: 搜索新闻
- calculator: 数学计算
- add_reminder: 添加提醒
- list_reminders: 列出提醒

**行为准则**：
1. 当用户问题涉及多个步骤时（例如“查北京天气，如果下雨就提醒我带伞”），请按顺序思考并调用工具。
2. 先获取必要信息，再给出最终回答。
3. 工具调用失败时，友好告知用户并尝试其他方式。
4. 回答应简洁、准确，不要编造未获取的信息。

**Few-shot 示例**：
用户：“帮我查一下上海天气，如果温度低于20度就建议穿外套。”
助手思考：1. 调用 get_weather(city="上海") → 得到"多云，温度 18°C..."
       2. 温度低于20度，最终回答“上海今天18度，建议穿外套保暖哦。”

用户：“设置一个明天上午9点的提醒，内容是开会。”
助手：调用 add_reminder(content="开会", remind_time="明天上午9点") → 确认添加成功。
""")

    prompt = ChatPromptTemplate.from_messages([
        system_prompt,
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=8
    )
    return executor

# ---------- 会话状态初始化 ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "hybrid_memory" not in st.session_state:
    st.session_state.hybrid_memory = HybridMemory(collection_name="assistant_memory", k_window=5)

# ---------- 渲染历史消息 ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- 用户输入 ----------
if prompt := st.chat_input("请输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 获取 Agent（传入后端固定变量）
    agent_executor = init_agent(API_KEY, BASE_URL, MODEL_NAME, temperature)

    hybrid_memory = st.session_state.hybrid_memory
    enhanced_context = hybrid_memory.get_enhanced_context(prompt)

    if enhanced_context:
        final_input = f"{enhanced_context}\n\n【当前问题】{prompt}"
    else:
        final_input = prompt

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                response = agent_executor.invoke({
                    "input": final_input,
                    "chat_history": hybrid_memory.window_memory.buffer_as_messages
                })
                answer = response["output"]
                st.markdown(answer)
            except Exception as e:
                answer = f"❌ 执行出错：{str(e)}"
                st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    hybrid_memory.save_interaction(prompt, answer)