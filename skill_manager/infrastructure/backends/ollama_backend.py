"""
Ollama 本地模型后端实现
"""
from typing import List, Dict, Any, Optional

from ...core.interfaces.llm_backend import ILLMBackend, IMessage, IModelConfig


class OllamaBackend(ILLMBackend):
    """
    Ollama 本地模型后端实现

    遵循依赖倒置原则 - 实现 ILLMBackend 接口
    """

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, config: Optional[IModelConfig] = None):
        import requests

        self.config = config or IModelConfig(
            model="llama3.2",
            base_url=self.DEFAULT_BASE_URL
        )
        self._requests = requests

    def complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """发送消息并获取响应"""
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        # 注意：Ollama 的工具调用支持有限，tools 参数暂不使用
        response = self._requests.post(
            f"{self.config.base_url}/api/chat",
            json={
                "model": self.config.model,
                "messages": full_messages,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def get_model_name(self) -> str:
        """获取模型名称"""
        return f"ollama/{self.config.model}"

    def configure(self, config: IModelConfig) -> None:
        """重新配置后端"""
        self.config = config
