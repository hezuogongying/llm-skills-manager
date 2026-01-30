# LLM Skills Manager

一个通用的 Python 库，用于解析和调用符合 [Agent Skills 规范](https://agentskills.io) 的 Skills，支持多种 LLM 后端。

## 特性

- ✅ 完全兼容 agentskills.io 规范
- ✅ 支持多种 LLM 后端：OpenAI、Anthropic Claude、Google Gemini、Ollama
- ✅ 自动 Skill 匹配（语义匹配）
- ✅ 支持多轮对话
- ✅ Skill 验证工具
- ✅ **SOLID 架构设计** - 易于测试和扩展
- ✅ 自动发现并加载 `skills/` 和 `.claude/skills/` 目录

## 安装

```bash
# 基础安装
pip install pyyaml

# 根据需要安装 LLM SDK
pip install openai          # OpenAI
pip install anthropic       # Anthropic Claude
pip install google-generativeai  # Google Gemini
pip install requests        # Ollama (使用 HTTP API)
```

## 使用说明

### 1. 配置环境变量

复制 `.env.example` 为 `.env` 并配置您的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，选择您要使用的后端：

```bash
# OpenAI
OPENAI_API_KEY=sk-your-api-key

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-api-key

# Google Gemini
GOOGLE_API_KEY=your-api-key

# Ollama (本地，无需 API 密钥)
# OLLAMA_BASE_URL=http://localhost:11434  # 可选
```

### 2. 基本使用

```python
from skill_manager import SkillManager, OpenAIBackend

# 初始化（自动加载 skills/ 和 .claude/skills/ 目录）
manager = SkillManager()

# 选择后端
backend = OpenAIBackend()

# 执行（自动匹配 Skill）
response = manager.execute("Review this code: def foo(): pass", backend)
print(response)
```

### 3. 创建 Skill

```python
from skill_manager import create_skill_template

skill_dir = create_skill_template(
    output_dir="./skills",
    name="code-review",
    description="Reviews code for bugs and security issues.",
    instructions="""# Code Review Skill

You are an expert code reviewer. Analyze code for:
- Security vulnerabilities
- Performance issues
- Best practices
"""
)
```

### 4. 自动发现 Skill

`SkillManager` 会自动从以下目录加载 Skills：

- `./skills/` - 当前工作目录下的 skills
- `./.claude/skills/` - Claude Code 的 skills 目录

```python
from skill_manager import SkillManager, OllamaBackend

# 自动发现并加载所有 skills
manager = SkillManager()

# 查看已加载的 skills
for meta in manager.list_skills():
    print(f"{meta.name}: {meta.description}")
```

### 5. 使用不同后端

```python
from skill_manager import (
    OpenAIBackend,
    AnthropicBackend,
    GoogleBackend,
    OllamaBackend
)

# OpenAI
backend = OpenAIBackend(model="gpt-4o")

# Anthropic Claude
backend = AnthropicBackend(model="claude-sonnet-4-20250514")

# Google Gemini
backend = GoogleBackend(model="gemini-2.0-flash")

# Ollama (本地)
backend = OllamaBackend(model="llama3.2")
```

#### Ollama 本地模型

1. 安装：访问 [ollama.ai](https://ollama.ai/) 或 `curl -fsSL https://ollama.ai/install.sh | sh`
2. 启动：`ollama serve`
3. 下载模型：`ollama pull llama3.2`
4. 使用：

```python
from skill_manager import SkillManager, OllamaBackend

backend = OllamaBackend(model="llama3.2")
manager = SkillManager()
response = manager.execute("Your question", backend)
```

## 架构设计

本项目采用 **SOLID 原则** 设计：

```
skill_manager/
├── core/                    # 领域层
│   ├── entities/            # 实体（Skill, Message）
│   ├── interfaces/          # 接口定义（ILLMBackend）
│   └── services/            # 领域服务
│       ├── skill_loader.py  # 加载 Skill
│       ├── skill_matcher.py # 匹配 Skill
│       ├── prompt_builder.py# 构建提示
│       └── skill_executor.py# 执行请求
├── infrastructure/          # 基础设施层
│   └── backends/            # LLM 后端实现
├── facades/                 # 外观模式
│   └── skill_manager.py     # SkillManager
└── utils.py                 # 便捷函数
```

### SOLID 原则

| 原则 | 说明 | 实现 |
|------|------|------|
| **S** 单一职责 | 每个类只负责一件事 | `SkillLoader` 只负责加载，`SkillMatcher` 只负责匹配 |
| **O** 开闭原则 | 对扩展开放，对修改关闭 | 通过 `ILLMBackend` 接口添加新后端 |
| **L** 里氏替换 | 实现可以替换基类 | 所有 `Backend` 实现可互换 |
| **I** 接口隔离 | 接口简洁明确 | `ILLMBackend` 只定义必要方法 |
| **D** 依赖倒置 | 依赖抽象而非具体 | 使用依赖注入 |

### 依赖注入

```python
from skill_manager import (
    SkillManager,
    ISkillMatcher,
    SemanticSkillMatcher
)

# 自定义匹配器
class MyMatcher(ISkillMatcher):
    def match(self, user_input, skills, backend):
        # 自定义匹配逻辑
        pass

# 使用依赖注入
manager = SkillManager(matcher=MyMatcher())
```

## API 参考

### SkillManager

```python
manager = SkillManager()

# 自动加载默认目录
manager.load_default_skills()

# 手动加载
manager.load_skill("./skills/my-skill")
manager.load_skills_from_directory("./skills")

# 获取 Skill
skill = manager.get_skill("my-skill")

# 执行
response = manager.execute(
    user_input="Your question",
    backend=backend,
    auto_match=True,
    skill_name=None,
    include_references=False,
    conversation_history=[]
)
```

### 验证 Skill

```python
from skill_manager import validate_skill

is_valid, errors = validate_skill("./skills/my-skill")
if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### 自定义后端

```python
from skill_manager import ILLMBackend, IModelConfig

class MyBackend(ILLMBackend):
    def complete(self, messages, system_prompt=None, tools=None):
        # 实现你的 LLM 调用逻辑
        pass

    def get_model_name(self):
        return "my-model"

    def configure(self, config: IModelConfig):
        # 配置逻辑
        pass
```

## Skill 规范

### 目录结构

```
my-skill/
├── SKILL.md          # 必需
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档
└── assets/          # 可选：资源文件
```

### SKILL.md 格式

```markdown
---
name: my-skill
description: What this does
---

# Skill Instructions

这里是 LLM 会收到的指令...
```

## 兼容性

此库创建的 Skills 与以下平台兼容：

| 平台 | 支持情况 |
|------|----------|
| Claude Code | ✅ |
| OpenAI Codex | ✅ |
| GitHub Copilot | ✅ |
| Cursor | ✅ |

## 测试

```bash
# 运行测试
python -m pytest tests/
```

## License

MIT License - 详见 [LICENSE](LICENSE) 文件
