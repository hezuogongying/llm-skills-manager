"""
Google Gemini 后端实现
"""
import os
from typing import List, Dict, Any, Optional

from ...core.interfaces.llm_backend import ILLMBackend, IMessage, IModelConfig


class GoogleBackend(ILLMBackend):
    """
    Google Gemini 后端实现

    遵循依赖倒置原则 - 实现 ILLMBackend 接口
    """

    def __init__(self, config: Optional[IModelConfig] = None):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("请安装 google-generativeai: pip install google-generativeai")

        self.config = config or IModelConfig(
            model="gemini-2.0-flash",
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        self._genai = genai
        genai.configure(api_key=self.config.api_key)
        self.model = genai.GenerativeModel(self.config.model)

    def complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """发送消息并获取响应"""
        # 转换消息格式
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [msg["content"]]})

        # Gemini 的 system prompt 通过 generation_config 设置
        config = {}
        if system_prompt:
            config["system_instruction"] = system_prompt
        if tools:
            config["tools"] = tools

        response = self.model.generate_content(contents, generation_config=config)
        return response.text

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model

    def configure(self, config: IModelConfig) -> None:
        """重新配置后端"""
        self.config = config
        self._genai.configure(api_key=config.api_key)
        self.model = self._genai.GenerativeModel(config.model)
