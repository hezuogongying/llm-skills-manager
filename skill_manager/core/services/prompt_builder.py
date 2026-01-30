"""
提示构建服务 - 单一职责原则

只负责构建系统提示和消息
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.skill import Skill
from ..entities.message import Message, MessageRole


class IPromptBuilder(ABC):
    """
    提示构建器接口

    遵循依赖倒置原则
    """

    @abstractmethod
    def build_system_prompt(
        self,
        skill: Optional[Skill],
        all_skills: List[Skill],
        include_references: bool = False
    ) -> Optional[str]:
        """构建系统提示"""
        pass

    @abstractmethod
    def build_messages(
        self,
        user_input: str,
        conversation_history: Optional[List[Message]] = None
    ) -> List[Message]:
        """构建消息列表"""
        pass


class SystemPromptBuilder(IPromptBuilder):
    """
    系统提示构建器

    遵循单一职责原则 - 只负责提示构建
    """

    def build_system_prompt(
        self,
        skill: Optional[Skill],
        all_skills: List[Skill],
        include_references: bool = False
    ) -> Optional[str]:
        """构建系统提示"""
        if skill:
            return self._build_skill_prompt(skill, include_references)
        else:
            return self._build_available_skills_prompt(all_skills)

    def build_messages(
        self,
        user_input: str,
        conversation_history: Optional[List[Message]] = None
    ) -> List[Message]:
        """构建消息列表"""
        messages = list(conversation_history) if conversation_history else []
        messages.append(Message(role=MessageRole.USER, content=user_input))
        return messages

    def _build_skill_prompt(self, skill: Skill, include_references: bool) -> str:
        """构建单个 Skill 的提示"""
        parts = [
            f"# Active Skill: {skill.metadata.name}\n",
            skill.instructions
        ]

        if include_references and skill.references:
            parts.append("\n\n# Reference Documents\n")
            for ref_name, ref in skill.references.items():
                parts.append(f"\n## {ref.name}\n{ref.content}")

        return "\n".join(parts)

    def _build_available_skills_prompt(self, skills: List[Skill]) -> Optional[str]:
        """构建可用 Skills 列表提示"""
        if not skills:
            return None

        lines = ["# Available Skills\n"]
        lines.append("The following skills are available. Use them when relevant:\n")

        for skill in skills:
            lines.append(f"- **{skill.metadata.name}**: {skill.metadata.description}")

        lines.append("\nTo use a skill, identify which one is most relevant to the task.")
        return "\n".join(lines)


class ToolCallPromptBuilder(IPromptBuilder):
    """
    函数调用提示构建器

    用于 function calling 模式的提示构建
    """

    def build_system_prompt(
        self,
        skill: Optional[Skill],
        all_skills: List[Skill],
        include_references: bool = False
    ) -> Optional[str]:
        """构建函数调用的系统提示"""
        return """You have access to specialized skills that can help with specific tasks.
When a skill is relevant to the user's request, activate it using the corresponding function.
If no skill is needed, respond directly."""

    def build_messages(
        self,
        user_input: str,
        conversation_history: Optional[List[Message]] = None
    ) -> List[Message]:
        """构建消息列表"""
        messages = list(conversation_history) if conversation_history else []
        messages.append(Message(role=MessageRole.USER, content=user_input))
        return messages

    def build_tools_definition(self, skills: List[Skill]) -> List[dict]:
        """构建 tools 定义列表"""
        tools = []
        for skill in skills:
            tools.append({
                "type": "function",
                "function": {
                    "name": f"activate_skill_{skill.metadata.name.replace('-', '_')}",
                    "description": skill.metadata.description,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            })
        return tools
