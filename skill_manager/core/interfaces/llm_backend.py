"""
LLM 后端接口 - 依赖倒置原则

高层模块（服务层）依赖这些抽象接口，而非具体实现
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class IMessage:
    """消息接口"""
    role: str
    content: str


@dataclass
class IModelConfig:
    """模型配置接口"""
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class ILLMBackend(ABC):
    """
    LLM 后端抽象接口

    遵循接口隔离原则 - 只定义必要的方法
    遵循依赖倒置原则 - 高层模块依赖此抽象
    """

    @abstractmethod
    def complete(
        self,
        messages: List[IMessage],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        发送消息并获取响应

        Args:
            messages: 消息列表
            system_prompt: 系统提示
            tools: 函数调用工具列表

        Returns:
            LLM 响应文本
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """获取当前模型名称"""
        pass

    @abstractmethod
    def configure(self, config: IModelConfig) -> None:
        """
        配置后端

        Args:
            config: 模型配置
        """
        pass
