"""
Anthropic Claude 后端实现
"""
import os
import logging
from typing import List, Dict, Any, Optional

from ...core.interfaces.llm_backend import ILLMBackend, IMessage, IModelConfig

logger = logging.getLogger(__name__)


class AnthropicBackend(ILLMBackend):
    """
    Anthropic Claude 后端实现

    遵循依赖倒置原则 - 实现 ILLMBackend 接口
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514"
    ):
        """
        初始化 Anthropic 后端

        Args:
            api_key: Anthropic API 密钥
            model: 模型名称
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError("请安装 anthropic: pip install anthropic")

        self.model = model
        self.client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )

        logger.info(f"✅ Anthropic backend initialized: model={self.model}")

    def complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """发送消息并获取响应"""
        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = tools

        logger.debug(f"📤 Sending {len(messages)} messages to Anthropic ({self.model})")

        response = self.client.messages.create(**kwargs)
        result = response.content[0].text

        logger.debug(f"📥 Received response from Anthropic: {len(result)} characters")
        return result

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.model

    def configure(self, config: IModelConfig) -> None:
        """重新配置后端"""
        self.model = config.model
        self.client = anthropic.Anthropic(api_key=config.api_key)
        logger.info(f"🔄 Anthropic backend reconfigured: model={self.model}")
