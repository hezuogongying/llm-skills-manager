"""
Anthropic Claude 后端实现
"""
import os
from typing import List, Dict, Any, Optional

from ...core.interfaces.llm_backend import ILLMBackend, IMessage, IModelConfig


class AnthropicBackend(ILLMBackend):
    """
    Anthropic Claude 后端实现

    遵循依赖倒置原则 - 实现 ILLMBackend 接口
    """

    def __init__(self, config: Optional[IModelConfig] = None):
        try:
            import anthropic
        except ImportError:
            raise ImportError("请安装 anthropic: pip install anthropic")

        self.config = config or IModelConfig(
            model="claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.client = anthropic.Anthropic(api_key=self.config.api_key)

    def complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """发送消息并获取响应"""
        kwargs = {
            "model": self.config.model,
            "max_tokens": 4096,
            "messages": messages
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model

    def configure(self, config: IModelConfig) -> None:
        """重新配置后端"""
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)
