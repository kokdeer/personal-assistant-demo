# memory_manager.py
import chromadb
from chromadb.config import Settings
from langchain.memory import ConversationBufferWindowMemory
from typing import List, Tuple

class HybridMemory:
    """混合记忆：短期窗口 + 向量检索长期历史"""
    def __init__(self, collection_name: str = "chat_history", k_window: int = 5):
        # 短期记忆：保留最近 k_window 轮对话
        self.window_memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=k_window
        )
        # 向量存储初始化
        self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        # 如果集合已存在则删除重建（简化，实际可复用）
        try:
            self.client.delete_collection(collection_name)
        except:
            pass
        self.collection = self.client.create_collection(collection_name)
        self.counter = 0

    def save_interaction(self, user_input: str, assistant_output: str):
        """将一轮对话存入向量库"""
        self.counter += 1
        text = f"用户：{user_input}\n助手：{assistant_output}"
        self.collection.add(
            documents=[text],
            ids=[str(self.counter)]
        )
        # 同时存入短期记忆（window_memory 自动管理）
        self.window_memory.save_context(
            {"input": user_input},
            {"output": assistant_output}
        )

    def get_enhanced_context(self, user_input: str, k_retrieve: int = 3) -> str:
        """检索相关历史对话片段，并与短期记忆组合为上下文"""
        # 1. 从向量库检索相似历史
        retrieved_texts = []
        if self.collection.count() > 0:
            results = self.collection.query(
                query_texts=[user_input],
                n_results=min(k_retrieve, self.collection.count())
            )
            retrieved_texts = results['documents'][0]

        # 2. 获取短期窗口消息（LangChain 格式）
        window_history = self.window_memory.load_memory_variables({}).get("chat_history", [])
        window_str = ""
        for msg in window_history:
            if msg.type == "human":
                window_str += f"用户：{msg.content}\n"
            else:
                window_str += f"助手：{msg.content}\n"

        # 3. 组合上下文
        context = ""
        if retrieved_texts:
            context += "【相关历史对话】\n" + "\n---\n".join(retrieved_texts) + "\n\n"
        if window_str:
            context += "【最近对话】\n" + window_str + "\n"
        return context.strip()

    def clear_window(self):
        """仅清空短期窗口（不影响向量库）"""
        self.window_memory.clear()