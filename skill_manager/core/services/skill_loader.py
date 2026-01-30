"""
Skill 加载服务 - 单一职责原则

只负责从文件系统加载 Skill
"""
import re
import yaml
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.skill import Skill, SkillMetadata, SkillScript, SkillReference
from ..interfaces.llm_backend import ILLMBackend


class ISkillLoader(ABC):
    """
    Skill 加载器接口

    遵循依赖倒置原则 - 服务依赖抽象而非具体实现
    """

    @abstractmethod
    def load_skill(self, skill_dir: Path) -> Skill:
        """加载单个 Skill"""
        pass

    @abstractmethod
    def load_skills_from_directory(self, base_dir: Path) -> List[Skill]:
        """从目录加载所有 Skills"""
        pass

    @abstractmethod
    def parse_skill_metadata(self, skill_md_path: Path) -> tuple[SkillMetadata, str]:
        """解析 SKILL.md 文件"""
        pass


class FilesystemSkillLoader(ISkillLoader):
    """
    文件系统 Skill 加载器

    遵循单一职责原则 - 只负责从文件系统加载
    """

    FRONTMATTER_PATTERN = re.compile(
        r'^---\s*\n(.*?)\n---\s*\n(.*)$',
        re.DOTALL
    )

    def parse_skill_metadata(self, skill_md_path: Path) -> tuple[SkillMetadata, str]:
        """解析 SKILL.md 文件"""
        content = skill_md_path.read_text(encoding='utf-8')
        return self._parse_content(content)

    def load_skill(self, skill_dir: Path) -> Skill:
        """加载单个 Skill"""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

        metadata, instructions = self.parse_skill_metadata(skill_md)

        # 加载脚本
        scripts = self._load_scripts(skill_dir)

        # 加载参考文档
        references = self._load_references(skill_dir)

        # 收集资源文件
        assets = self._load_assets(skill_dir)

        return Skill(
            metadata=metadata,
            instructions=instructions,
            path=skill_dir,
            scripts=scripts,
            references=references,
            assets=assets
        )

    def load_skills_from_directory(self, base_dir: Path) -> List[Skill]:
        """从目录加载所有 Skills"""
        loaded = []

        for item in base_dir.iterdir():
            if item.is_dir():
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    try:
                        skill = self.load_skill(item)
                        loaded.append(skill)
                    except Exception as e:
                        print(f"Warning: Failed to load skill from {item}: {e}")

        return loaded

    def _parse_content(self, content: str) -> tuple[SkillMetadata, str]:
        """解析 SKILL.md 内容"""
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            raise ValueError("Invalid SKILL.md format: missing YAML frontmatter")

        yaml_content = match.group(1)
        markdown_content = match.group(2).strip()

        # 解析 YAML
        data = yaml.safe_load(yaml_content)
        if not isinstance(data, dict):
            raise ValueError("Invalid YAML frontmatter")

        # 验证必填字段
        if 'name' not in data:
            raise ValueError("Missing required field: name")
        if 'description' not in data:
            raise ValueError("Missing required field: description")

        # 验证 name 格式
        name = data['name']
        if len(name) > 64:
            raise ValueError("name must be <= 64 characters")
        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', name):
            raise ValueError("name must be lowercase letters, numbers, and hyphens only")

        # 验证 description 格式
        description = data['description']
        if len(description) > 1024:
            raise ValueError("description must be <= 1024 characters")

        # 提取 metadata 中的额外字段
        known_fields = {
            'name', 'description', 'license', 'version', 'author',
            'allowed-tools', 'allowed_tools', 'compatibility', 'metadata'
        }
        extra_metadata = {k: v for k, v in data.items() if k not in known_fields}

        metadata = SkillMetadata(
            name=name,
            description=description,
            license=data.get('license'),
            version=data.get('version') or data.get('metadata', {}).get('version'),
            author=data.get('author') or data.get('metadata', {}).get('author'),
            allowed_tools=data.get('allowed-tools') or data.get('allowed_tools'),
            compatibility=data.get('compatibility'),
            metadata={**data.get('metadata', {}), **extra_metadata}
        )

        return metadata, markdown_content

    def _load_scripts(self, skill_dir: Path) -> dict:
        """加载脚本文件"""
        scripts = {}
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.iterdir():
                if script_file.is_file():
                    ext = script_file.suffix.lower()
                    language_map = {
                        '.py': 'python',
                        '.sh': 'bash',
                        '.js': 'javascript',
                    }
                    scripts[script_file.name] = SkillScript(
                        name=script_file.stem,
                        content=script_file.read_text(encoding='utf-8'),
                        path=script_file,
                        language=language_map.get(ext, 'unknown')
                    )
        return scripts

    def _load_references(self, skill_dir: Path) -> dict:
        """加载参考文档"""
        references = {}

        # 从 references 目录加载
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in refs_dir.iterdir():
                if ref_file.is_file() and ref_file.suffix.lower() == '.md':
                    references[ref_file.name] = SkillReference(
                        name=ref_file.stem,
                        content=ref_file.read_text(encoding='utf-8'),
                        path=ref_file
                    )

        # 同时检查根目录下的 .md 文件
        for md_file in skill_dir.glob("*.md"):
            if md_file.name != "SKILL.md" and md_file.name not in references:
                references[md_file.name] = SkillReference(
                    name=md_file.stem,
                    content=md_file.read_text(encoding='utf-8'),
                    path=md_file
                )

        return references

    def _load_assets(self, skill_dir: Path) -> List[Path]:
        """收集资源文件"""
        assets = []
        assets_dir = skill_dir / "assets"
        if assets_dir.exists():
            assets = list(assets_dir.iterdir())
        return assets
