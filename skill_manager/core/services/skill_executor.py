"""
Skill 执行服务 - 单一职责原则

只负责协调执行流程
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.skill import Skill
from ..entities.message import Message
from ..interfaces.llm_backend import ILLMBackend
from .skill_matcher import ISkillMatcher
from .prompt_builder import IPromptBuilder


class ISkillExecutor(ABC):
    """
    Skill 执行器接口

    遵循依赖倒置原则
    """

    @abstractmethod
    def execute(
        self,
        user_input: str,
        backend: ILLMBackend,
        skills: List[Skill],
        conversation_history: Optional[List[Message]] = None,
        auto_match: bool = True,
        skill_name: Optional[str] = None,
        include_references: bool = False
    ) -> str:
        """
        执行用户请求

        Args:
            user_input: 用户输入
            backend: LLM 后端
            skills: 可用 Skill 列表
            conversation_history: 对话历史
            auto_match: 是否自动匹配 Skill
            skill_name: 指定使用的 Skill 名称
            include_references: 是否包含参考文档

        Returns:
            LLM 响应
        """
        pass


class SkillExecutor(ISkillExecutor):
    """
    Skill 执行器

    遵循单一职责原则 - 只负责协调执行流程
    使用依赖注入 - 注入 Matcher 和 Builder
    """

    def __init__(
        self,
        matcher: ISkillMatcher,
        prompt_builder: IPromptBuilder
    ):
        """
        Args:
            matcher: Skill 匹配器
            prompt_builder: 提示构建器
        """
        self.matcher = matcher
        self.prompt_builder = prompt_builder

    def execute(
        self,
        user_input: str,
        backend: ILLMBackend,
        skills: List[Skill],
        conversation_history: Optional[List[Message]] = None,
        auto_match: bool = True,
        skill_name: Optional[str] = None,
        include_references: bool = False
    ) -> str:
        """执行用户请求"""
        # 确定使用哪个 Skill
        skill = self._select_skill(
            user_input,
            skills,
            backend,
            auto_match,
            skill_name
        )

        # 构建系统提示
        system_prompt = self.prompt_builder.build_system_prompt(
            skill,
            skills,
            include_references
        )

        # 构建消息
        messages = self.prompt_builder.build_messages(
            user_input,
            conversation_history
        )

        # 调用 LLM
        llm_messages = [msg.to_llm_format() for msg in messages]
        return backend.complete(llm_messages, system_prompt=system_prompt)

    def _select_skill(
        self,
        user_input: str,
        skills: List[Skill],
        backend: ILLMBackend,
        auto_match: bool,
        skill_name: Optional[str]
    ) -> Optional[Skill]:
        """选择要使用的 Skill"""
        if skill_name:
            # 按名称查找
            skill_map = {s.metadata.name: s for s in skills}
            skill = skill_map.get(skill_name)
            if not skill:
                raise ValueError(f"Skill not found: {skill_name}")
            return skill

        if auto_match:
            # 自动匹配
            return self.matcher.match(user_input, skills, backend)

        return None


class ToolCallExecutor(ISkillExecutor):
    """
    函数调用模式执行器

    使用 function calling 而非系统提示注入
    """

    def __init__(self, prompt_builder: IPromptBuilder):
        """
        Args:
            prompt_builder: 提示构建器
        """
        self.prompt_builder = prompt_builder

    def execute(
        self,
        user_input: str,
        backend: ILLMBackend,
        skills: List[Skill],
        conversation_history: Optional[List[Message]] = None,
        auto_match: bool = True,
        skill_name: Optional[str] = None,
        include_references: bool = False
    ) -> str:
        """使用函数调用模式执行"""
        # 构建 tools 定义
        if hasattr(self.prompt_builder, 'build_tools_definition'):
            tools = self.prompt_builder.build_tools_definition(skills)
        else:
            tools = None

        # 构建系统提示
        system_prompt = self.prompt_builder.build_system_prompt(
            None,
            skills,
            include_references
        )

        # 构建消息
        messages = self.prompt_builder.build_messages(
            user_input,
            conversation_history
        )

        # 调用 LLM
        llm_messages = [msg.to_llm_format() for msg in messages]
        return backend.complete(
            llm_messages,
            system_prompt=system_prompt,
            tools=tools
        )
