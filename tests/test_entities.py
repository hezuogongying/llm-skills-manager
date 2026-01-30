"""
测试实体模块
"""
import unittest
from pathlib import Path
from skill_manager.core.entities.skill import Skill, SkillMetadata, SkillScript, SkillReference
from skill_manager.core.entities.message import Message, MessageRole


class TestSkillMetadata(unittest.TestCase):
    """测试 SkillMetadata 实体"""

    def test_creation(self):
        """测试创建 SkillMetadata"""
        metadata = SkillMetadata(
            name="test-skill",
            description="A test skill"
        )
        self.assertEqual(metadata.name, "test-skill")
        self.assertEqual(metadata.description, "A test skill")

    def test_to_dict(self):
        """测试转换为字典"""
        metadata = SkillMetadata(
            name="test-skill",
            description="A test skill",
            license="MIT",
            version="1.0.0"
        )
        data = metadata.to_dict()
        self.assertEqual(data["name"], "test-skill")
        self.assertEqual(data["description"], "A test skill")
        self.assertEqual(data["license"], "MIT")
        self.assertEqual(data["version"], "1.0.0")


class TestMessage(unittest.TestCase):
    """测试 Message 实体"""

    def test_creation(self):
        """测试创建 Message"""
        message = Message(
            role=MessageRole.USER,
            content="Hello"
        )
        self.assertEqual(message.role, MessageRole.USER)
        self.assertEqual(message.content, "Hello")

    def test_to_dict(self):
        """测试转换为字典"""
        message = Message(
            role=MessageRole.USER,
            content="Hello"
        )
        data = message.to_dict()
        self.assertEqual(data["role"], "user")
        self.assertEqual(data["content"], "Hello")

    def test_from_dict(self):
        """测试从字典创建"""
        data = {"role": "user", "content": "Hello"}
        message = Message.from_dict(data)
        self.assertEqual(message.role, MessageRole.USER)
        self.assertEqual(message.content, "Hello")

    def test_to_llm_format(self):
        """测试转换为 LLM 格式"""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Hi there"
        )
        data = message.to_llm_format()
        self.assertEqual(data["role"], "assistant")
        self.assertEqual(data["content"], "Hi there")


class TestSkill(unittest.TestCase):
    """测试 Skill 实体"""

    def test_creation(self):
        """测试创建 Skill"""
        metadata = SkillMetadata(
            name="test-skill",
            description="A test skill"
        )
        skill = Skill(
            metadata=metadata,
            instructions="Test instructions",
            path=Path("/tmp/test")
        )
        self.assertEqual(skill.metadata.name, "test-skill")
        self.assertEqual(skill.instructions, "Test instructions")

    def test_full_content(self):
        """测试获取完整内容"""
        metadata = SkillMetadata(
            name="test-skill",
            description="A test skill"
        )
        skill = Skill(
            metadata=metadata,
            instructions="Test instructions",
            path=Path("/tmp/test")
        )
        self.assertEqual(skill.full_content, "Test instructions")


if __name__ == "__main__":
    unittest.main()
