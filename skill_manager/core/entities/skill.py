"""
Skill 实体 - 单一职责原则

只负责数据存储，业务逻辑由服务层处理
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class SkillMetadata:
    """
    Skill 元数据

    遵循单一职责原则 - 只负责元数据存储
    """
    name: str
    description: str
    license: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    allowed_tools: Optional[List[str]] = None
    compatibility: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "license": self.license,
            "version": self.version,
            "author": self.author,
            "allowed_tools": self.allowed_tools,
            "compatibility": self.compatibility,
            "metadata": self.metadata,
        }


@dataclass
class SkillScript:
    """
    Skill 脚本实体

    遵循单一职责原则 - 只负责脚本元数据
    """
    name: str
    content: str
    path: Path
    language: str  # python, bash, javascript, etc.


@dataclass
class SkillReference:
    """
    Skill 参考文档实体

    遵循单一职责原则 - 只负责参考文档元数据
    """
    name: str
    content: str
    path: Path


@dataclass
class Skill:
    """
    Skill 实体

    遵循单一职责原则 - 只负责数据聚合
    执行逻辑由 SkillExecutor 服务处理
    """
    metadata: SkillMetadata
    instructions: str
    path: Path
    scripts: Dict[str, SkillScript] = field(default_factory=dict)
    references: Dict[str, SkillReference] = field(default_factory=dict)
    assets: List[Path] = field(default_factory=list)

    @property
    def full_content(self) -> str:
        """获取完整的 Skill 内容"""
        return self.instructions

    def get_reference(self, name: str) -> Optional[SkillReference]:
        """获取参考文档"""
        return self.references.get(name)

    def get_script(self, name: str) -> Optional[SkillScript]:
        """获取脚本"""
        return self.scripts.get(name)

    def list_reference_names(self) -> List[str]:
        """列出所有参考文档名称"""
        return list(self.references.keys())

    def list_script_names(self) -> List[str]:
        """列出所有脚本名称"""
        return list(self.scripts.keys())
