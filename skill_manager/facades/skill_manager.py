"""
SkillManager 外观类 - 外观模式

提供简化的 API，内部使用依赖注入的 SOLID 架构
"""
from pathlib import Path
from typing import Optional, List, Dict

from ..core.entities.skill import Skill, SkillMetadata
from ..core.entities.message import Message, MessageRole
from ..core.interfaces.llm_backend import ILLMBackend
from ..core.services.skill_loader import ISkillLoader, FilesystemSkillLoader
from ..core.services.skill_matcher import ISkillMatcher, SemanticSkillMatcher
from ..core.services.prompt_builder import IPromptBuilder, SystemPromptBuilder, ToolCallPromptBuilder
from ..core.services.skill_executor import ISkillExecutor, SkillExecutor, ToolCallExecutor


class SkillManager:
    """
    Skill 管理器外观类

    提供简化的 API，内部使用 SOLID 架构：
    - 依赖注入：通过构造函数注入依赖
    - 单一职责：每个服务只负责一件事
    - 接口隔离：依赖抽象接口而非具体实现

    使用示例：
        from skill_manager import SkillManager, OpenAIBackend

        manager = SkillManager()
        backend = OpenAIBackend()
        response = manager.execute("帮我处理 PDF", backend)
    """

    # 默认的 Skill 搜索目录
    DEFAULT_SKILL_DIRS = [
        "skills",
        ".claude/skills",
    ]

    def __init__(
        self,
        loader: Optional[ISkillLoader] = None,
        matcher: Optional[ISkillMatcher] = None,
        prompt_builder: Optional[IPromptBuilder] = None,
        executor: Optional[ISkillExecutor] = None,
        auto_load: bool = True
    ):
        """
        初始化 SkillManager

        Args:
            loader: Skill 加载器
            matcher: Skill 匹配器
            prompt_builder: 提示构建器
            executor: 执行器
            auto_load: 是否自动加载默认目录
        """
        self._loader = loader or FilesystemSkillLoader()
        self._matcher = matcher or SemanticSkillMatcher()
        self._prompt_builder = prompt_builder or SystemPromptBuilder()

        self._executor = executor or SkillExecutor(
            matcher=self._matcher,
            prompt_builder=self._prompt_builder
        )

        self._skills: Dict[str, Skill] = {}

        if auto_load:
            self.load_default_skills()

    # ========================================================================
    # Skill 加载方法
    # ========================================================================

    def load_default_skills(self) -> List[Skill]:
        """自动加载默认目录中的 Skills"""
        loaded = []
        for skill_dir in self.DEFAULT_SKILL_DIRS:
            path = Path(skill_dir)
            if path.exists() and path.is_dir():
                try:
                    skills = self.load_skills_from_directory(path)
                    loaded.extend(skills)
                except Exception:
                    pass
        return loaded

    def load_skill(self, skill_dir: str | Path) -> Skill:
        """加载单个 Skill"""
        skill_dir = Path(skill_dir)
        skill = self._loader.load_skill(skill_dir)
        self._skills[skill.metadata.name] = skill
        return skill

    def load_skills_from_directory(self, base_dir: str | Path) -> List[Skill]:
        """从目录加载所有 Skills"""
        base_dir = Path(base_dir)
        skills = self._loader.load_skills_from_directory(base_dir)
        for skill in skills:
            self._skills[skill.metadata.name] = skill
        return skills

    def get_skill(self, name: str) -> Optional[Skill]:
        """获取指定名称的 Skill"""
        return self._skills.get(name)

    def list_skills(self) -> List[SkillMetadata]:
        """列出所有已加载的 Skills 元数据"""
        return [s.metadata for s in self._skills.values()]

    # ========================================================================
    # 执行方法
    # ========================================================================

    def execute(
        self,
        user_input: str,
        backend: ILLMBackend,
        auto_match: bool = True,
        skill_name: Optional[str] = None,
        include_references: bool = False,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """执行用户请求"""
        history = None
        if conversation_history:
            history = [
                Message(
                    role=MessageRole(msg["role"]),
                    content=msg["content"]
                )
                for msg in conversation_history
            ]

        return self._executor.execute(
            user_input=user_input,
            backend=backend,
            skills=list(self._skills.values()),
            conversation_history=history,
            auto_match=auto_match,
            skill_name=skill_name,
            include_references=include_references
        )

    def execute_with_tools(
        self,
        user_input: str,
        backend: ILLMBackend,
        additional_tools: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """使用 function calling 执行"""
        tool_builder = ToolCallPromptBuilder()
        tool_executor = ToolCallExecutor(tool_builder)

        history = None
        if conversation_history:
            history = [
                Message(
                    role=MessageRole(msg["role"]),
                    content=msg["content"]
                )
                for msg in conversation_history
            ]

        tools = tool_builder.build_tools_definition(list(self._skills.values()))
        if additional_tools:
            tools.extend(additional_tools)

        system_prompt = tool_builder.build_system_prompt(None, list(self._skills.values()))
        messages = tool_builder.build_messages(user_input, history)
        llm_messages = [msg.to_llm_format() for msg in messages]

        return backend.complete(llm_messages, system_prompt=system_prompt, tools=tools)

    # ========================================================================
    # 便捷方法
    # ========================================================================

    def get_skills_system_prompt(self) -> str:
        """生成包含所有 Skills 描述的系统提示"""
        prompt = self._prompt_builder.build_system_prompt(
            skill=None,
            all_skills=list(self._skills.values())
        )
        return prompt or ""

    def match_skill(self, user_input: str, backend: ILLMBackend) -> Optional[Skill]:
        """使用 LLM 匹配最合适的 Skill"""
        return self._matcher.match(
            user_input=user_input,
            skills=list(self._skills.values()),
            backend=backend
        )
