"""
Ollama 本地模型后端实现
"""
import logging
from typing import List, Dict, Any, Optional

from ...core.interfaces.llm_backend import ILLMBackend, IMessage, IModelConfig

# 配置日志
logger = logging.getLogger(__name__)


class OllamaBackend(ILLMBackend):
    """
    Ollama 本地模型后端实现

    遵循依赖倒置原则 - 实现 ILLMBackend 接口
    """

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: Optional[str] = None,
        config: Optional[IModelConfig] = None
    ):
        """
        初始化 Ollama 后端

        Args:
            model: 模型名称（如 "llama3.2", "qwen2.5"）
            base_url: Ollama 服务地址
            config: 模型配置（可选，优先使用 model 和 base_url 参数）
        """
        import requests

        # 如果提供了 config，使用它；否则创建新的
        if config:
            self.config = config
        else:
            self.config = IModelConfig(
                model=model,
                base_url=base_url or self.DEFAULT_BASE_URL
            )

        self._requests = requests
        logger.info(f"✅ Ollama backend initialized: model={self.config.model}, base_url={self.config.base_url}")

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

        logger.debug(f"📤 Sending {len(messages)} messages to Ollama ({self.config.model})")

        # 注意：Ollama 的工具调用支持有限，tools 参数暂不使用
        response = self._requests.post(
            f"{self.config.base_url}/api/chat",
            json={
                "model": self.config.model,
                "messages": full_messages,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()["message"]["content"]

        logger.debug(f"📥 Received response from Ollama: {len(result)} characters")
        return result

    def get_model_name(self) -> str:
        """获取模型名称"""
        return f"ollama/{self.config.model}"

    def configure(self, config: IModelConfig) -> None:
        """重新配置后端"""
        self.config = config
        logger.info(f"🔄 Ollama backend reconfigured: model={config.model}")
