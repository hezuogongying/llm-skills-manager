"""
OpenAI 后端实现

实现 ILLMBackend 接口
"""
import os
import logging
from typing import List, Dict, Any, Optional

from ...core.interfaces.llm_backend import ILLMBackend, IMessage, IModelConfig

logger = logging.getLogger(__name__)


class OpenAIBackend(ILLMBackend):
    """
    OpenAI 后端实现

    遵循依赖倒置原则 - 实现 ILLMBackend 接口
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        base_url: Optional[str] = None
    ):
        """
        初始化 OpenAI 后端

        Args:
            api_key: OpenAI API 密钥
            model: 模型名称
            base_url: API 基础 URL（可选）
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

        self.model = model
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url
        )

        logger.info(f"✅ OpenAI backend initialized: model={self.model}")

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

        kwargs = {"model": self.model, "messages": full_messages}
        if tools:
            kwargs["tools"] = tools

        logger.debug(f"📤 Sending {len(messages)} messages to OpenAI ({self.model})")

        response = self.client.chat.completions.create(**kwargs)
        result = response.choices[0].message.content

        logger.debug(f"📥 Received response from OpenAI: {len(result)} characters")
        return result

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.model

    def configure(self, config: IModelConfig) -> None:
        """重新配置后端"""
        self.model = config.model
        logger.info(f"🔄 OpenAI backend reconfigured: model={self.model}")
