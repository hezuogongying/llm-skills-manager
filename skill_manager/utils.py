"""
便捷函数 - 创建和验证 Skill 模板
"""
import re
from pathlib import Path
from typing import List, Tuple

from .core.services.skill_loader import FilesystemSkillLoader


def create_skill_template(
    output_dir: str | Path,
    name: str,
    description: str,
    instructions: str = "# Instructions\n\nAdd your skill instructions here.",
    include_scripts: bool = False,
    include_references: bool = False,
    include_assets: bool = False
) -> Path:
    """
    创建 Skill 模板目录

    Args:
        output_dir: 输出目录
        name: Skill 名称
        description: Skill 描述
        instructions: 指令内容
        include_scripts: 是否创建 scripts 目录
        include_references: 是否创建 references 目录
        include_assets: 是否创建 assets 目录

    Returns:
        创建的 Skill 目录路径
    """
    output_dir = Path(output_dir)
    skill_dir = output_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # 创建 SKILL.md
    skill_md = skill_dir / "SKILL.md"
    content = f"""---
name: {name}
description: {description}
---

{instructions}
"""
    skill_md.write_text(content, encoding='utf-8')

    # 创建可选目录
    if include_scripts:
        (skill_dir / "scripts").mkdir(exist_ok=True)
        # 创建示例脚本
        example_script = skill_dir / "scripts" / "example.py"
        example_script.write_text('#!/usr/bin/env python3\nprint("Hello from skill script!")\n')

    if include_references:
        (skill_dir / "references").mkdir(exist_ok=True)

    if include_assets:
        (skill_dir / "assets").mkdir(exist_ok=True)

    return skill_dir


def validate_skill(skill_dir: str | Path) -> Tuple[bool, List[str]]:
    """
    验证 Skill 目录是否符合规范

    Args:
        skill_dir: Skill 目录路径

    Returns:
        (是否有效, 错误消息列表)
    """
    skill_dir = Path(skill_dir)
    errors = []

    # 检查 SKILL.md 是否存在
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    try:
        loader = FilesystemSkillLoader()
        metadata, _ = loader.parse_skill_metadata(skill_md)
    except Exception as e:
        errors.append(f"Failed to parse SKILL.md: {e}")
        return False, errors

    # 验证名称
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', metadata.name):
        errors.append("name must contain only lowercase letters, numbers, and hyphens")

    if len(metadata.name) > 64:
        errors.append("name must be <= 64 characters")

    # 验证描述
    if len(metadata.description) > 1024:
        errors.append("description must be <= 1024 characters")

    return len(errors) == 0, errors
