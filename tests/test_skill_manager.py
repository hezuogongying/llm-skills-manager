"""
测试 SkillManager 外观类
"""
import unittest
import tempfile
import shutil
from pathlib import Path
from skill_manager import SkillManager
from skill_manager.core.interfaces.llm_backend import ILLMBackend, IModelConfig


class MockBackend(ILLMBackend):
    """模拟后端用于测试"""

    def complete(self, messages, system_prompt=None, tools=None):
        return "Mock response"

    def get_model_name(self):
        return "mock-model"

    def configure(self, config):
        pass


class TestSkillManager(unittest.TestCase):
    """测试 SkillManager"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.backend = MockBackend()

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

    def test_init_no_auto_load(self):
        """测试初始化时不自动加载"""
        manager = SkillManager(auto_load=False)
        self.assertEqual(len(manager.list_skills()), 0)

    def test_load_skill(self):
        """测试加载单个 Skill"""
        skill_dir = self._create_skill("test-skill", "A test skill")

        manager = SkillManager(auto_load=False)
        manager.load_skill(skill_dir)

        self.assertEqual(len(manager.list_skills()), 1)
        self.assertEqual(manager.list_skills()[0].name, "test-skill")

    def test_load_skills_from_directory(self):
        """测试从目录加载 Skills"""
        self._create_skill("skill1", "First skill")
        self._create_skill("skill2", "Second skill")

        manager = SkillManager(auto_load=False)
        manager.load_skills_from_directory(Path(self.test_dir))

        self.assertEqual(len(manager.list_skills()), 2)

    def test_get_skill(self):
        """测试获取指定 Skill"""
        skill_dir = self._create_skill("test-skill", "A test skill")

        manager = SkillManager(auto_load=False)
        manager.load_skill(skill_dir)

        skill = manager.get_skill("test-skill")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.metadata.name, "test-skill")

    def test_execute(self):
        """测试执行"""
        skill_dir = self._create_skill("test-skill", "A test skill")

        manager = SkillManager(auto_load=False)
        manager.load_skill(skill_dir)

        response = manager.execute(
            "Test input",
            self.backend,
            auto_match=False
        )

        self.assertEqual(response, "Mock response")

    def test_default_skill_dirs(self):
        """测试默认目录列表"""
        self.assertEqual(
            SkillManager.DEFAULT_SKILL_DIRS,
            ["skills", ".claude/skills"]
        )


if __name__ == "__main__":
    unittest.main()
