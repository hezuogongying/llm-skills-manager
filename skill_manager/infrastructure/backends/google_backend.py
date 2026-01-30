"""
Google Gemini 后端实现
"""
import os
import logging
from typing import List, Dict, Any, Optional

from ...core.interfaces.llm_backend import ILLMBackend, IMessage, IModelConfig

logger = logging.getLogger(__name__)


class GoogleBackend(ILLMBackend):
    """
    Google Gemini 后端实现

    遵循依赖倒置原则 - 实现 ILLMBackend 接口
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash"
    ):
        """
        初始化 Google 后端

        Args:
            api_key: Google API 密钥
            model: 模型名称
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("请安装 google-generativeai: pip install google-generativeai")

        self.model_name = model
        self._genai = genai
        genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model)

        logger.info(f"✅ Google backend initialized: model={self.model_name}")

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

        logger.debug(f"📤 Sending {len(messages)} messages to Google ({self.model_name})")

        response = self.model.generate_content(contents, generation_config=config)
        result = response.text

        logger.debug(f"📥 Received response from Google: {len(result)} characters")
        return result

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.model_name

    def configure(self, config: IModelConfig) -> None:
        """重新配置后端"""
        self.model_name = config.model
        self._genai.configure(api_key=config.api_key)
        self.model = self._genai.GenerativeModel(config.model)
        logger.info(f"🔄 Google backend reconfigured: model={self.model_name}")
