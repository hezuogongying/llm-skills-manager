# LLM Skills Manager

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![SOLID](https://img.shields.io/badge/Design-SOLID-orange.svg)](https://en.wikipedia.org/wiki/SOLID)

一个通用的 Python 库，用于解析和调用符合 [Agent Skills 规范](https://agentskills.io) 的 Skills，支持多种 LLM 后端。

[GitHub](https://github.com/hezuogongying/llm-skills-manager) | [Gitee](https://gitee.com/hezuo_111_admin/llm-skills-manager)

</div>

---

## ✨ 特性

- ✅ **完全兼容** agentskills.io 规范
- ✅ **多后端支持** - OpenAI、Anthropic Claude、Google Gemini、Ollama
- ✅ **智能匹配** - 自动语义匹配最合适的 Skill
- ✅ **多轮对话** - 支持对话历史管理
- ✅ **SOLID 架构** - 单一职责、依赖注入、易于测试
- ✅ **自动发现** - 自动加载 `skills/` 和 `.claude/skills/` 目录
- ✅ **Web 界面** - 基于 Streamlit 的可视化应用
- ✅ **单元测试** - 完整的测试覆盖

---

## 📦 安装

```bash
# 基础依赖
pip install pyyaml

# LLM SDK（根据需要选择）
pip install openai               # OpenAI
pip install anthropic            # Anthropic Claude
pip install google-generativeai  # Google Gemini
pip install requests             # Ollama

# Web 应用（可选）
pip install streamlit
```

---

## 🚀 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# OpenAI
OPENAI_API_KEY=sk-your-api-key

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-api-key

# Google Gemini
GOOGLE_API_KEY=your-api-key

# Ollama (本地运行，无需 API Key)
# OLLAMA_BASE_URL=http://localhost:11434
```

### 2. 基本使用

```python
from skill_manager import SkillManager, OllamaBackend

# 初始化（自动加载 skills/ 和 .claude/skills/）
manager = SkillManager()

# 选择后端
backend = OllamaBackend(model="llama3.2")

# 执行（自动匹配 Skill）
response = manager.execute("帮我审查这段代码", backend)
print(response)
```

### 3. 创建 Skill

```python
from skill_manager import create_skill_template

skill_dir = create_skill_template(
    output_dir="./skills",
    name="code-review",
    description="代码审查专家，发现安全漏洞和性能问题",
    instructions="""# Code Review Skill

你是一位资深代码审查专家，专注于：
- 安全漏洞（SQL注入、XSS等）
- 性能问题
- 代码规范
"""
)
```

### 4. 使用不同后端

```python
from skill_manager import (
    OpenAIBackend,
    AnthropicBackend,
    GoogleBackend,
    OllamaBackend
)

# OpenAI GPT-4
backend = OpenAIBackend(model="gpt-4o")

# Anthropic Claude
backend = AnthropicBackend(model="claude-sonnet-4-20250514")

# Google Gemini
backend = GoogleBackend(model="gemini-2.0-flash")

# Ollama 本地
backend = OllamaBackend(model="llama3.2")
```

---

## 🎯 Ollama 本地模型

无需 API Key，完全本地运行：

```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. 启动服务
ollama serve

# 3. 下载模型
ollama pull llama3.2

# 4. 使用
python -c "
from skill_manager import SkillManager, OllamaBackend
manager = SkillManager()
backend = OllamaBackend(model='llama3.2')
print(manager.execute('你好', backend))
"
```

---

## 🏗️ 架构设计

本项目严格遵循 **SOLID 原则**：

```
skill_manager/
├── core/                    # 领域层
│   ├── entities/            # 实体（Skill, Message）
│   ├── interfaces/          # 接口定义（依赖倒置）
│   └── services/            # 领域服务（单一职责）
│       ├── skill_loader.py  # 加载 Skill
│       ├── skill_matcher.py # 语义匹配 Skill
│       ├── prompt_builder.py# 构建系统提示
│       └── skill_executor.py# 执行请求
├── infrastructure/          # 基础设施层
│   └── backends/            # LLM 后端实现
├── facades/                 # 外观模式
│   └── skill_manager.py     # SkillManager
├── utils.py                 # 便捷函数
└── webapp.py                # Streamlit Web 应用
```

### SOLID 原则

| 原则 | 说明 | 实现 |
|:---:|------|------|
| **S** 单一职责 | 每个类只负责一件事 | `SkillLoader` 只加载，`SkillMatcher` 只匹配 |
| **O** 开闭原则 | 对扩展开放，对修改关闭 | 通过 `ILLMBackend` 接口添加新后端 |
| **L** 里氏替换 | 实现可替换基类 | 所有 `Backend` 可互换 |
| **I** 接口隔离 | 接口简洁明确 | `ILLMBackend` 只定义必要方法 |
| **D** 依赖倒置 | 依赖抽象而非具体 | 使用依赖注入 |

### 依赖注入

```python
from skill_manager import SkillManager, ISkillMatcher, SemanticSkillMatcher

# 自定义匹配器
class MyMatcher(ISkillMatcher):
    def match(self, user_input, skills, backend):
        # 自定义匹配逻辑
        return skills[0] if skills else None

# 注入自定义组件
manager = SkillManager(matcher=MyMatcher())
```

---

## 💻 Web 应用

### 功能特性

- 💬 **智能对话** - 多轮对话，自动匹配 Skill
- 📚 **Skill 管理** - 创建、加载、验证、删除
- ⚙️ **后端配置** - 可视化配置 LLM 后端

### 启动

```bash
streamlit run webapp.py
```

访问 http://localhost:8501

---

## 📖 API 参考

### SkillManager

```python
from skill_manager import SkillManager

manager = SkillManager()

# 加载 Skills
manager.load_default_skills()              # 自动加载默认目录
manager.load_skill("./skills/my-skill")    # 加载单个
manager.load_skills_from_directory("./skills")  # 批量加载

# 获取 Skill
skill = manager.get_skill("my-skill")

# 列出所有 Skills
for meta in manager.list_skills():
    print(f"{meta.name}: {meta.description}")

# 执行
response = manager.execute(
    user_input="Your question",
    backend=backend,
    auto_match=True,           # 自动匹配
    skill_name=None,           # 或指定 Skill
    include_references=False,  # 包含参考文档
    conversation_history=[]    # 对话历史
)
```

### 验证 Skill

```python
from skill_manager import validate_skill

is_valid, errors = validate_skill("./skills/my-skill")
if not is_valid:
    for error in errors:
        print(f"❌ {error}")
```

### 自定义后端

```python
from skill_manager import ILLMBackend, IModelConfig

class MyBackend(ILLMBackend):
    def complete(self, messages, system_prompt=None, tools=None):
        # 实现 LLM 调用
        return "Response"

    def get_model_name(self):
        return "my-model"

    def configure(self, config: IModelConfig):
        # 配置逻辑
        pass
```

---

## 📋 Skill 规范

### 目录结构

```
my-skill/
├── SKILL.md          # 必需：主文件
├── scripts/          # 可选：可执行脚本
│   ├── helper.py
│   └── setup.sh
├── references/       # 可选：参考文档
│   └── api.md
└── assets/          # 可选：资源文件
    └── template.json
```

### SKILL.md 格式

```markdown
---
name: my-skill          # 必需：小写字母、数字、连字符
description: What this does   # 必需：简要描述
version: "1.0.0"        # 可选：版本号
author: your-name        # 可选：作者
---

# Skill Instructions

这里是 LLM 会收到的指令...
```

---

## 🧪 测试

```bash
# 运行所有测试
python -m unittest discover tests/

# 运行特定测试
python -m unittest tests.test_skill_manager

# 查看覆盖率
python -m coverage run -m unittest discover tests/
python -m coverage report
```

---

## 🔗 兼容性

此库创建的 Skills 与以下平台兼容：

| 平台 | 支持情况 |
|------|:--------:|
| Claude Code | ✅ |
| OpenAI Codex | ✅ |
| GitHub Copilot | ✅ |
| Cursor | ✅ |
| VS Code | ✅ |

---

## 📄 License

[MIT License](LICENSE)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hezuogongying/llm-skills-manager&type=Date)](https://star-history.com/#hezuogongying/llm-skills-manager&Date)

---

<div align="center">

**如果这个项目对你有帮助，请给个 Star ⭐**

Made with ❤️ by [LLM Skills Manager](https://github.com/hezuogongying/llm-skills-manager)

</div>
