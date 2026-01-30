"""
OpenAI 后端实现

实现 ILLMBackend 接口
"""
import os
from typing import List, Dict, Any, Optional

from ...core.interfaces.llm_backend import ILLMBackend, IMessage, IModelConfig


class OpenAIBackend(ILLMBackend):
    """
    OpenAI 后端实现

    遵循依赖倒置原则 - 实现 ILLMBackend 接口
    """

    def __init__(self, config: Optional[IModelConfig] = None):
        """
        Args:
            config: 模型配置，如果为 None 则使用默认配置
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

        self.config = config or IModelConfig(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )

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

        kwargs = {"model": self.config.model, "messages": full_messages}
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model

    def configure(self, config: IModelConfig) -> None:
        """重新配置后端"""
        self.config = config
