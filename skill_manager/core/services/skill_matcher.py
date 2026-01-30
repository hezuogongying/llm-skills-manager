"""
Skill 匹配服务 - 单一职责原则

只负责根据用户输入匹配合适的 Skill
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.skill import Skill
from ..interfaces.llm_backend import ILLMBackend, IMessage


class ISkillMatcher(ABC):
    """
    Skill 匹配器接口

    遵循依赖倒置原则 - 依赖抽象接口
    """

    @abstractmethod
    def match(
        self,
        user_input: str,
        skills: List[Skill],
        backend: ILLMBackend
    ) -> Optional[Skill]:
        """
        匹配最合适的 Skill

        Args:
            user_input: 用户输入
            skills: 可用 Skill 列表
            backend: LLM 后端（用于语义匹配）

        Returns:
            匹配的 Skill，如果没有匹配则返回 None
        """
        pass


class SemanticSkillMatcher(ISkillMatcher):
    """
    语义 Skill 匹配器

    使用 LLM 进行语义匹配，理解用户意图

    遵循单一职责原则 - 只负责语义匹配逻辑
    """

    def __init__(self, threshold: float = 0.5):
        """
        Args:
            threshold: 匹配阈值（预留，当前使用 LLM 直接匹配）
        """
        self.threshold = threshold

    def match(
        self,
        user_input: str,
        skills: List[Skill],
        backend: ILLMBackend
    ) -> Optional[Skill]:
        """使用语义匹配找到最合适的 Skill"""
        if not skills:
            return None

        # 构建技能列表描述
        skill_descriptions = "\n".join([
            f"- {skill.metadata.name}: {skill.metadata.description}"
            for skill in skills
        ])

        # 构建匹配提示
        prompt = f"""Based on the user's request, determine which skill (if any) is most relevant.

Available skills:
{skill_descriptions}

User request: {user_input}

Respond with ONLY the skill name (e.g., "pdf" or "docx") if a skill matches, or "none" if no skill is relevant.
Do not include any explanation."""

        # 调用 LLM 进行匹配
        messages = [IMessage(role="user", content=prompt)]
        response = backend.complete([message.to_llm_format() for message in messages])

        # 清理响应
        response = response.strip().lower().replace('"', '').replace("'", "").strip()

        if response == "none":
            return None

        # 查找匹配的 Skill
        skill_map = {skill.metadata.name: skill for skill in skills}
        return skill_map.get(response)


class ExactSkillMatcher(ISkillMatcher):
    """
    精确关键词匹配器

    不使用 LLM，基于关键词匹配

    遵循单一职责原则 - 只负责关键词匹配
    """

    def __init__(self, keywords: dict[str, list[str]] = None):
        """
        Args:
            keywords: 技能名到关键词列表的映射
        """
        self.keywords = keywords or {}

    def add_keywords(self, skill_name: str, words: list[str]):
        """添加关键词"""
        if skill_name not in self.keywords:
            self.keywords[skill_name] = []
        self.keywords[skill_name].extend(words)

    def match(
        self,
        user_input: str,
        skills: List[Skill],
        backend: ILLMBackend
    ) -> Optional[Skill]:
        """使用关键词匹配"""
        user_input_lower = user_input.lower()

        # 计算匹配分数
        best_skill = None
        best_score = 0

        for skill in skills:
            score = self._calculate_score(user_input_lower, skill)
            if score > best_score:
                best_score = score
                best_skill = skill

        return best_skill if best_score > 0 else None

    def _calculate_score(self, user_input: str, skill: Skill) -> int:
        """计算匹配分数"""
        score = 0

        # 检查名称匹配
        if skill.metadata.name in user_input:
            score += 10

        # 检查关键词匹配
        keywords = self.keywords.get(skill.metadata.name, [])
        for keyword in keywords:
            if keyword.lower() in user_input:
                score += 1

        return score
