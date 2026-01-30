"""
Agent Skills Manager 使用示例

这个文件展示了如何使用 skill_manager.py 来：
1. 加载和管理 Skills
2. 与不同 LLM 后端集成
3. 自动匹配和执行 Skills
"""

from pathlib import Path


def example_basic_usage():
    """基础用法示例"""
    from skill_manager import SkillManager, SkillParser, create_skill_template
    
    # 1. 创建一个简单的 Skill
    print("="*60)
    print("1. 创建 Skill")
    print("="*60)
    
    skill_dir = create_skill_template(
        output_dir="./my_skills",
        name="python-helper",
        description="Helps with Python programming tasks, debugging, and best practices.",
        instructions="""# Python Helper Skill

You are an expert Python developer. Help users with:

## Debugging
- Analyze error messages
- Suggest fixes
- Explain stack traces

## Best Practices
- PEP 8 style guide
- Type hints
- Documentation

## Common Tasks
- File I/O
- Data processing
- API integration

Always provide working code examples.
"""
    )
    print(f"Created skill at: {skill_dir}")
    
    # 2. 加载 Skill
    print("\n" + "="*60)
    print("2. 加载 Skill")
    print("="*60)
    
    manager = SkillManager()
    skill = manager.load_skill(skill_dir)
    
    print(f"Skill name: {skill.metadata.name}")
    print(f"Description: {skill.metadata.description}")
    print(f"Instructions length: {len(skill.instructions)} chars")
    
    # 3. 列出所有 Skills
    print("\n" + "="*60)
    print("3. 列出所有 Skills")
    print("="*60)
    
    for meta in manager.list_skills():
        print(f"- {meta.name}: {meta.description[:50]}...")
    
    return manager


def example_with_openai():
    """使用 OpenAI 后端的示例"""
    from skill_manager import SkillManager, OpenAIBackend, create_skill_template
    import os
    
    print("\n" + "="*60)
    print("OpenAI 后端示例")
    print("="*60)
    
    # 检查 API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  请设置 OPENAI_API_KEY 环境变量")
        print("   export OPENAI_API_KEY='your-api-key'")
        return
    
    # 创建 Skills
    create_skill_template(
        output_dir="./my_skills",
        name="sql-expert",
        description="Helps with SQL queries, database design, and optimization.",
        instructions="""# SQL Expert Skill

You are a database expert. Help users with:

- Writing efficient SQL queries
- Database schema design
- Query optimization
- Explaining execution plans

Support: MySQL, PostgreSQL, SQLite
"""
    )
    
    # 加载并使用
    manager = SkillManager()
    manager.load_skills_from_directory("./my_skills")
    
    backend = OpenAIBackend(model="gpt-4o-mini")  # 或 "gpt-4o"
    
    # 自动匹配 Skill 并执行
    user_input = "How do I write a query to find duplicate rows in a table?"
    response = manager.execute(user_input, backend)
    
    print(f"User: {user_input}")
    print(f"Response: {response[:500]}...")


def example_with_anthropic():
    """使用 Anthropic Claude 后端的示例"""
    from skill_manager import SkillManager, AnthropicBackend
    import os
    
    print("\n" + "="*60)
    print("Anthropic Claude 后端示例")
    print("="*60)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  请设置 ANTHROPIC_API_KEY 环境变量")
        print("   export ANTHROPIC_API_KEY='your-api-key'")
        return
    
    manager = SkillManager()
    manager.load_skills_from_directory("./my_skills")
    
    backend = AnthropicBackend(model="claude-sonnet-4-20250514")
    
    # 指定使用特定 Skill
    response = manager.execute(
        "Explain Python decorators with an example",
        backend,
        skill_name="python-helper"  # 明确指定 Skill
    )
    
    print(f"Response: {response[:500]}...")


def example_with_ollama():
    """使用 Ollama 本地模型的示例"""
    from skill_manager import SkillManager, OllamaBackend
    
    print("\n" + "="*60)
    print("Ollama 本地模型示例")
    print("="*60)
    
    print("确保 Ollama 正在运行: ollama serve")
    print("确保已下载模型: ollama pull llama3.2")
    
    manager = SkillManager()
    manager.load_skills_from_directory("./my_skills")
    
    try:
        backend = OllamaBackend(model="llama3.2")
        
        response = manager.execute(
            "What is a Python list comprehension?",
            backend,
            auto_match=False  # 不自动匹配，直接回答
        )
        
        print(f"Response: {response[:500]}...")
    except Exception as e:
        print(f"Error: {e}")
        print("请确保 Ollama 正在运行")


def example_custom_backend():
    """创建自定义后端的示例"""
    from skill_manager import LLMBackend, SkillManager
    from typing import List, Dict, Optional
    
    print("\n" + "="*60)
    print("自定义后端示例")
    print("="*60)
    
    class MockBackend(LLMBackend):
        """模拟后端（用于测试）"""
        
        def complete(
            self, 
            messages: List[Dict[str, str]], 
            system_prompt: Optional[str] = None,
            tools: Optional[List[Dict]] = None
        ) -> str:
            # 返回模拟响应
            user_msg = messages[-1]["content"] if messages else ""
            has_skill = system_prompt and "Active Skill" in system_prompt
            
            return f"""[Mock Response]
User asked: {user_msg[:100]}...
Skill active: {has_skill}
System prompt length: {len(system_prompt) if system_prompt else 0} chars
"""
        
        def get_model_name(self) -> str:
            return "mock-model"
    
    # 使用自定义后端
    manager = SkillManager()
    manager.load_skills_from_directory("./my_skills")
    
    backend = MockBackend()
    response = manager.execute("Test query", backend)
    
    print(response)


def example_conversation():
    """多轮对话示例"""
    from skill_manager import SkillManager, OpenAIBackend
    import os
    
    print("\n" + "="*60)
    print("多轮对话示例")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  需要 OPENAI_API_KEY")
        return
    
    manager = SkillManager()
    manager.load_skills_from_directory("./my_skills")
    
    backend = OpenAIBackend()
    
    # 对话历史
    history = []
    
    # 第一轮
    user_msg1 = "I have a list of numbers: [1, 2, 3, 4, 5]. How do I double each number?"
    response1 = manager.execute(
        user_msg1, 
        backend,
        conversation_history=history
    )
    history.append({"role": "user", "content": user_msg1})
    history.append({"role": "assistant", "content": response1})
    
    print(f"User: {user_msg1}")
    print(f"Assistant: {response1[:300]}...\n")
    
    # 第二轮（继续对话）
    user_msg2 = "Now how do I filter to keep only numbers greater than 5?"
    response2 = manager.execute(
        user_msg2,
        backend,
        conversation_history=history
    )
    
    print(f"User: {user_msg2}")
    print(f"Assistant: {response2[:300]}...")


def example_parse_skill():
    """解析现有 Skill 的示例"""
    from skill_manager import SkillParser
    
    print("\n" + "="*60)
    print("解析 SKILL.md 示例")
    print("="*60)
    
    skill_content = """---
name: my-awesome-skill
description: This is a demo skill that shows the YAML frontmatter format.
license: MIT
metadata:
  author: example-user
  version: "1.0.0"
  tags:
    - demo
    - example
---

# My Awesome Skill

This is the instruction content that the LLM will receive.

## Usage

Use this skill when you need to do awesome things.

## Examples

```python
print("Hello from the skill!")
```
"""
    
    metadata, instructions = SkillParser.parse_content(skill_content)
    
    print(f"Name: {metadata.name}")
    print(f"Description: {metadata.description}")
    print(f"License: {metadata.license}")
    print(f"Version: {metadata.version}")
    print(f"Author: {metadata.author}")
    print(f"Metadata: {metadata.metadata}")
    print(f"\nInstructions preview:\n{instructions[:200]}...")


def example_validate_skill():
    """验证 Skill 的示例"""
    from skill_manager import validate_skill, create_skill_template
    
    print("\n" + "="*60)
    print("验证 Skill 示例")
    print("="*60)
    
    # 创建一个有效的 Skill
    valid_dir = create_skill_template(
        output_dir="./test_skills",
        name="valid-skill",
        description="A valid skill for testing."
    )
    
    is_valid, errors = validate_skill(valid_dir)
    print(f"valid-skill: {'✅ VALID' if is_valid else '❌ INVALID'}")
    
    # 手动创建一个无效的 Skill
    invalid_dir = Path("./test_skills/Invalid_Skill")  # 名称包含大写字母
    invalid_dir.mkdir(parents=True, exist_ok=True)
    (invalid_dir / "SKILL.md").write_text("""---
name: Invalid_Skill
description: This skill has an invalid name with uppercase letters.
---
Instructions here.
""")
    
    is_valid, errors = validate_skill(invalid_dir)
    print(f"Invalid_Skill: {'✅ VALID' if is_valid else '❌ INVALID'}")
    if errors:
        for e in errors:
            print(f"  - {e}")


if __name__ == "__main__":
    print("Agent Skills Manager 使用示例")
    print("="*60)
    
    # 运行基础示例
    manager = example_basic_usage()
    
    # 解析示例
    example_parse_skill()
    
    # 验证示例
    example_validate_skill()
    
    # 自定义后端示例
    example_custom_backend()
    
    print("\n" + "="*60)
    print("完成！")
    print("="*60)
    print("""
要使用真实的 LLM 后端，请设置相应的 API key：

OpenAI:
  export OPENAI_API_KEY='your-key'
  然后取消注释并运行 example_with_openai()

Anthropic:
  export ANTHROPIC_API_KEY='your-key'
  然后取消注释并运行 example_with_anthropic()

Ollama (本地):
  ollama serve
  ollama pull llama3.2
  然后取消注释并运行 example_with_ollama()
""")
