"""
消息实体 - 单一职责原则

只负责数据存储，不包含业务逻辑
"""
from dataclasses import dataclass
from enum import Enum


class MessageRole(Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """
    消息实体

    遵循单一职责原则 - 只负责数据封装
    """
    role: MessageRole
    content: str

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {"role": self.role.value, "content": self.content}

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """从字典创建消息"""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"]
        )

    def to_llm_format(self) -> dict:
        """转换为 LLM API 格式"""
        return {"role": self.role.value, "content": self.content}
