# LLM Skills Manager

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![SOLID](https://img.shields.io/badge/Design-SOLID-orange.svg)](https://en.wikipedia.org/wiki/SOLID)

A universal Python library for parsing and invoking [Agent Skills](https://agentskills.io) with support for multiple LLM backends.

[GitHub](https://github.com/hezuogongying/llm-skills-manager) | [Gitee](https://gitee.com/hezuo_111_admin/llm-skills-manager)

</div>

---

## Features

- ✅ **Fully Compatible** with agentskills.io specification
- ✅ **Multi-Backend Support** - OpenAI, Anthropic Claude, Google Gemini, Ollama
- ✅ **Smart Matching** - Automatic semantic skill matching
- ✅ **Multi-turn Conversations** - Conversation history support
- ✅ **SOLID Architecture** - Single responsibility, dependency injection, testable
- ✅ **Auto-discovery** - Automatically loads `skills/` and `.claude/skills/` directories
- ✅ **Web Interface** - Streamlit-based visual application
- ✅ **Unit Tests** - Complete test coverage

---

## Installation

```bash
# Core dependencies
pip install pyyaml

# LLM SDKs (choose as needed)
pip install openai               # OpenAI
pip install anthropic            # Anthropic Claude
pip install google-generativeai  # Google Gemini
pip install requests             # Ollama

# Web application (optional)
pip install streamlit
```

---

## Quick Start

### 1. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-api-key

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-api-key

# Google Gemini
GOOGLE_API_KEY=your-api-key

# Ollama (local, no API Key needed)
# OLLAMA_BASE_URL=http://localhost:11434
```

### 2. Basic Usage

```python
from skill_manager import SkillManager, OllamaBackend

# Initialize (auto-loads skills/ and .claude/skills/)
manager = SkillManager()

# Select backend
backend = OllamaBackend(model="llama3.2")

# Execute (auto-matches skill)
response = manager.execute("Review this code for me", backend)
print(response)
```

### 3. Create a Skill

```python
from skill_manager import create_skill_template

skill_dir = create_skill_template(
    output_dir="./skills",
    name="code-review",
    description="Expert code reviewer for security and performance issues",
    instructions="""# Code Review Skill

You are a senior code reviewer focusing on:
- Security vulnerabilities (SQL injection, XSS, etc.)
- Performance issues
- Code standards
"""
)
```

### 4. Using Different Backends

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

# Ollama local
backend = OllamaBackend(model="llama3.2")
```

---

## Ollama Local Models

Run completely locally without API keys:

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start service
ollama serve

# 3. Download model
ollama pull llama3.2

# 4. Use
python -c "
from skill_manager import SkillManager, OllamaBackend
manager = SkillManager()
backend = OllamaBackend(model='llama3.2')
print(manager.execute('Hello', backend))
"
```

---

## Architecture

This project strictly follows **SOLID principles**:

```
skill_manager/
├── core/                    # Domain layer
│   ├── entities/            # Entities (Skill, Message)
│   ├── interfaces/          # Interface definitions (Dependency Inversion)
│   └── services/            # Domain services (Single Responsibility)
│       ├── skill_loader.py  # Load skills
│       ├── skill_matcher.py # Semantic skill matching
│       ├── prompt_builder.py# Build system prompts
│       └── skill_executor.py# Execute requests
├── infrastructure/          # Infrastructure layer
│   └── backends/            # LLM backend implementations
├── facades/                 # Facade pattern
│   └── skill_manager.py     # SkillManager
├── utils.py                 # Utility functions
└── webapp.py                # Streamlit web app
```

### SOLID Principles

| Principle | Description | Implementation |
|:---:|-----------|----------------|
| **S** Single Responsibility | Each class does one thing | `SkillLoader` only loads, `SkillMatcher` only matches |
| **O** Open/Closed | Open for extension, closed for modification | Add backends via `ILLMBackend` interface |
| **L** Liskov Substitution | Implementations can replace base class | All `Backend` implementations are swappable |
| **I** Interface Segregation | Interfaces are clean and focused | `ILLMBackend` defines only necessary methods |
| **D** Dependency Inversion | Depend on abstractions, not concretions | Use dependency injection |

### Dependency Injection

```python
from skill_manager import SkillManager, ISkillMatcher, SemanticSkillMatcher

# Custom matcher
class MyMatcher(ISkillMatcher):
    def match(self, user_input, skills, backend):
        # Custom matching logic
        return skills[0] if skills else None

# Inject custom components
manager = SkillManager(matcher=MyMatcher())
```

---

## Web Application

### Features

- 💬 **Smart Chat** - Multi-turn conversations with auto skill matching
- 📚 **Skill Management** - Create, load, validate, delete skills
- ⚙️ **Backend Config** - Visual LLM backend configuration

### Launch

```bash
streamlit run webapp.py
```

Visit http://localhost:8501

---

## API Reference

### SkillManager

```python
from skill_manager import SkillManager

manager = SkillManager()

# Load skills
manager.load_default_skills()              # Auto-load default directories
manager.load_skill("./skills/my-skill")    # Load single skill
manager.load_skills_from_directory("./skills")  # Batch load

# Get skill
skill = manager.get_skill("my-skill")

# List all skills
for meta in manager.list_skills():
    print(f"{meta.name}: {meta.description}")

# Execute
response = manager.execute(
    user_input="Your question",
    backend=backend,
    auto_match=True,           # Auto-match skill
    skill_name=None,           # Or specify skill
    include_references=False,  # Include reference docs
    conversation_history=[]    # Conversation history
)
```

### Validate Skill

```python
from skill_manager import validate_skill

is_valid, errors = validate_skill("./skills/my-skill")
if not is_valid:
    for error in errors:
        print(f"❌ {error}")
```

### Custom Backend

```python
from skill_manager import ILLMBackend, IModelConfig

class MyBackend(ILLMBackend):
    def complete(self, messages, system_prompt=None, tools=None):
        # Implement LLM call
        return "Response"

    def get_model_name(self):
        return "my-model"

    def configure(self, config: IModelConfig):
        # Configuration logic
        pass
```

---

## Skill Specification

### Directory Structure

```
my-skill/
├── SKILL.md          # Required: Main file
├── scripts/          # Optional: Executable scripts
│   ├── helper.py
│   └── setup.sh
├── references/       # Optional: Reference docs
│   └── api.md
└── assets/          # Optional: Asset files
    └── template.json
```

### SKILL.md Format

```markdown
---
name: my-skill          # Required: lowercase, numbers, hyphens
description: What this does   # Required: Short description
version: "1.0.0"        # Optional: Version
author: your-name        # Optional: Author
---

# Skill Instructions

Instructions that LLM will receive...
```

---

## Testing

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test
python -m unittest tests.test_skill_manager

# View coverage
python -m coverage run -m unittest discover tests/
python -m coverage report
```

---

## Compatibility

Skills created with this library are compatible with:

| Platform | Support |
|----------|:-------:|
| Claude Code | ✅ |
| OpenAI Codex | ✅ |
| GitHub Copilot | ✅ |
| Cursor | ✅ |
| VS Code | ✅ |

---

## License

[MIT License](LICENSE)

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hezuogongying/llm-skills-manager&type=Date)](https://star-history.com/#hezuogongying/llm-skills-manager&Date)

---

<div align="center">

**If this project helps you, please give it a Star ⭐**

Made with ❤️ by [LLM Skills Manager](https://github.com/hezuogongying/llm-skills-manager)

</div>
