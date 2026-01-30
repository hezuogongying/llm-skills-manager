"""
测试 Skill 加载服务
"""
import unittest
import tempfile
import shutil
from pathlib import Path
from skill_manager.core.services.skill_loader import FilesystemSkillLoader
from skill_manager.core.entities.skill import SkillMetadata


class TestFilesystemSkillLoader(unittest.TestCase):
    """测试 FilesystemSkillLoader"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.loader = FilesystemSkillLoader()

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir)

    def _create_skill(self, name: str, description: str) -> Path:
        """创建测试 Skill"""
        skill_dir = Path(self.test_dir) / name
        skill_dir.mkdir(parents=True)

        content = f"""---
name: {name}
description: {description}
---

# Instructions

This is a test skill.
"""
        (skill_dir / "SKILL.md").write_text(content)
        return skill_dir

    def test_load_skill(self):
        """测试加载单个 Skill"""
        skill_dir = self._create_skill("test-skill", "A test skill")

        skill = self.loader.load_skill(skill_dir)

        self.assertEqual(skill.metadata.name, "test-skill")
        self.assertEqual(skill.metadata.description, "A test skill")
        self.assertIn("instructions", skill.instructions.lower())

    def test_load_skill_with_references(self):
        """测试加载带参考文档的 Skill"""
        skill_dir = self._create_skill("test-skill", "A test skill")

        # 创建参考文档
        refs_dir = skill_dir / "references"
        refs_dir.mkdir()
        (refs_dir / "api.md").write_text("# API Reference")

        skill = self.loader.load_skill(skill_dir)

        self.assertIn("api.md", skill.references)
        self.assertEqual(skill.references["api.md"].content, "# API Reference")

    def test_load_skill_with_scripts(self):
        """测试加载带脚本的 Skill"""
        skill_dir = self._create_skill("test-skill", "A test skill")

        # 创建脚本
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "helper.py").write_text("print('hello')")

        skill = self.loader.load_skill(skill_dir)

        self.assertIn("helper.py", skill.scripts)
        self.assertEqual(skill.scripts["helper.py"].language, "python")

    def test_load_skills_from_directory(self):
        """测试从目录加载多个 Skills"""
        self._create_skill("skill1", "First skill")
        self._create_skill("skill2", "Second skill")

        skills = self.loader.load_skills_from_directory(Path(self.test_dir))

        self.assertEqual(len(skills), 2)
        skill_names = {s.metadata.name for s in skills}
        self.assertEqual(skill_names, {"skill1", "skill2"})


if __name__ == "__main__":
    unittest.main()
