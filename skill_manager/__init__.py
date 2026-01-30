"""
Agent Skills Manager - 通用的 Agent Skills 解析和调用库

支持 agentskills.io 规范，可以与多种 LLM 后端集成：
- OpenAI (GPT-4, GPT-4o)
- Anthropic (Claude)
- Google (Gemini)
- 本地模型 (Ollama)

架构特点（v2.0 SOLID 重构）：
- **S** - 单一职责原则：每个服务类只负责一件事
- **O** - 开闭原则：通过接口扩展，无需修改现有代码
- **L** - 里氏替换原则：所有后端实现可互换
- **I** - 接口隔离原则：接口简洁明确
- **D** - 依赖倒置原则：使用依赖注入，高层模块依赖抽象

使用示例：
    from skill_manager import SkillManager, OpenAIBackend

    manager = SkillManager()
    manager.load_skills_from_directory("./skills")

    backend = OpenAIBackend()
    response = manager.execute("帮我处理这个 PDF 文件", backend)
"""

# ============================================================================
# 导出外观类（主要 API）
# ============================================================================
from .facades import SkillManager
from .core.entities.message import MessageRole

# ============================================================================
# 导出 LLM 后端实现
# ============================================================================
from .infrastructure.backends import (
    OpenAIBackend,
    AnthropicBackend,
    GoogleBackend,
    OllamaBackend
)

# ============================================================================
# 导出接口（用于依赖注入和扩展）
# ============================================================================
from .core.interfaces import ILLMBackend, IModelConfig, IMessage

# ============================================================================
# 导出实体（用于类型注解）
# ============================================================================
from .core.entities import Skill, SkillMetadata, Message

# ============================================================================
# 导出服务接口（用于自定义实现）
# ============================================================================
from .core.services import (
    ISkillLoader,
    ISkillMatcher,
    IPromptBuilder,
    ISkillExecutor,
    FilesystemSkillLoader,
    SemanticSkillMatcher,
    SystemPromptBuilder,
    SkillExecutor,
)

# ============================================================================
# 便捷函数
# ============================================================================
from .utils import create_skill_template, validate_skill

# ============================================================================
# 日志配置
# ============================================================================
from .infrastructure.config.logging_config import setup_logging, get_logger

# ============================================================================
# 版本信息
# ============================================================================
__version__ = "2.0.0"
__author__ = "LLM Skills Manager Contributors"

__all__ = [
    # 主要 API
    'SkillManager',

    # 后端实现
    'OpenAIBackend',
    'AnthropicBackend',
    'GoogleBackend',
    'OllamaBackend',

    # 接口
    'ILLMBackend',
    'IModelConfig',
    'IMessage',

    # 实体
    'Skill',
    'SkillMetadata',
    'Message',
    'MessageRole',

    # 服务接口
    'ISkillLoader',
    'ISkillMatcher',
    'IPromptBuilder',
    'ISkillExecutor',

    # 服务实现
    'FilesystemSkillLoader',
    'SemanticSkillMatcher',
    'SystemPromptBuilder',
    'SkillExecutor',

    # 便捷函数
    'create_skill_template',
    'validate_skill',

    # 日志配置
    'setup_logging',
    'get_logger',
]
