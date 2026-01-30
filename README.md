# Agent Skills Manager

一个通用的 Python 库，用于解析和调用符合 [Agent Skills 规范](https://agentskills.io) 的 Skills，支持多种 LLM 后端。

## 特性

- ✅ 完全兼容 agentskills.io 规范
- ✅ 支持多种 LLM 后端：OpenAI、Anthropic Claude、Google Gemini、Ollama
- ✅ 自动 Skill 匹配（语义匹配）
- ✅ 支持多轮对话
- ✅ Skill 验证工具
- ✅ 易于测试和扩展
- ✅ **SOLID 架构设计**

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

## 环境配置

复制 `.env.example` 为 `.env` 并配置您的 API 密钥：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入您需要使用的 LLM 服务配置：

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

## 架构设计

本项目采用模块化架构便于测试和扩展：

```
skill_manager/
├── core/                    # 领域层（核心业务逻辑）
│   ├── entities/            # 实体（数据结构）
│   │   ├── skill.py         # Skill 实体
│   │   └── message.py       # Message 实体
│   ├── interfaces/          # 接口定义（依赖倒置）
│   │   └── llm_backend.py   # ILLMBackend 接口
│   └── services/            # 领域服务（单一职责）
│       ├── skill_loader.py      # 加载 Skill
│       ├── skill_matcher.py     # 匹配 Skill
│       ├── prompt_builder.py    # 构建提示
│       └── skill_executor.py    # 执行请求
├── infrastructure/          # 基础设施层（外部集成）
│   └── backends/            # LLM 后端实现
│       ├── openai_backend.py
│       ├── anthropic_backend.py
│       ├── google_backend.py
│       └── ollama_backend.py
├── facades/                 # 外观模式（简化 API）
│   └── skill_manager.py     # SkillManager 外观类
└── utils.py                 # 便捷函数
```

### SOLID 原则应用

| 原则 | 说明 | 实现 |
|------|------|------|
| **S** 单一职责 | 每个类只负责一件事 | `SkillLoader` 只负责加载，`SkillMatcher` 只负责匹配 |
| **O** 开闭原则 | 对扩展开放，对修改关闭 | 通过 `ILLMBackend` 接口添加新后端 |
| **L** 里氏替换 | 实现可以替换基类 | 所有 `Backend` 实现可互换 |
| **I** 接口隔离 | 接口简洁明确 | `ILLMBackend` 只定义必要方法 |
| **D** 依赖倒置 | 依赖抽象而非具体 | 使用依赖注入，高层模块依赖接口 |

### 依赖注入示例

```python
from skill_manager import (
    SkillManager,
    ISkillMatcher,
    IPromptBuilder,
    SemanticSkillMatcher,
    SystemPromptBuilder
)

# 自定义匹配器
class MyMatcher(ISkillMatcher):
    def match(self, user_input, skills, backend):
        # 自定义匹配逻辑
        pass

# 使用依赖注入
manager = SkillManager(
    matcher=MyMatcher(),
    prompt_builder=SystemPromptBuilder()
)
```

## 快速开始

### 1. 创建 Skill

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

或手动创建 `skills/code-review/SKILL.md`:

```markdown
---
name: code-review
description: Reviews code for bugs and security issues.
---

# Code Review Skill

You are an expert code reviewer...
```

### 2. 加载并使用 Skill

```python
from skill_manager import SkillManager, OpenAIBackend

# 初始化
manager = SkillManager()
manager.load_skills_from_directory("./skills")

# 选择后端
backend = OpenAIBackend(api_key="your-api-key")

# 执行（自动匹配 Skill）
response = manager.execute(
    "Review this code: def foo(): pass",
    backend
)
print(response)
```

### 3. 使用不同后端

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
backend = OllamaBackend(model="llama3.2", base_url="http://localhost:11434")
```

#### Ollama 本地模型使用

Ollama 让您可以在本地运行开源大模型，无需 API 密钥。

1. **安装 Ollama**：
   - 访问 [ollama.ai](https://ollama.ai/) 下载安装
   - 或使用命令行：`curl -fsSL https://ollama.ai/install.sh | sh`

2. **启动服务**：
   ```bash
   ollama serve
   ```

3. **下载模型**：
   ```bash
   # Llama 3.2 (推荐)
   ollama pull llama3.2

   # 其他可用模型
   ollama pull qwen2.5       # 通义千问
   ollama pull mistral       # Mistral
   ollama pull codellama     # Code Llama
   ```

4. **使用示例**：
   ```python
   from skill_manager import SkillManager, OllamaBackend

   backend = OllamaBackend(model="llama3.2")
   manager = SkillManager()
   manager.load_skills_from_directory("./skills")

   response = manager.execute("Your question", backend)
   ```

## API 参考

### SkillManager

主要的 Skill 管理类。

```python
manager = SkillManager()

# 加载 Skills
manager.load_skill("./skills/my-skill")
manager.load_skills_from_directory("./skills")

# 获取 Skill
skill = manager.get_skill("my-skill")

# 列出所有 Skills
for meta in manager.list_skills():
    print(f"{meta.name}: {meta.description}")

# 执行
response = manager.execute(
    user_input="Your question",
    backend=backend,
    auto_match=True,           # 自动匹配 Skill
    skill_name=None,           # 或指定 Skill 名称
    include_references=False,  # 包含参考文档
    conversation_history=[]    # 对话历史
)
```

### SkillParser

解析 SKILL.md 文件。

```python
from skill_manager import SkillParser

# 解析文件
metadata, instructions = SkillParser.parse_file(Path("./SKILL.md"))

# 解析内容字符串
metadata, instructions = SkillParser.parse_content(content)

# 加载完整 Skill（包含脚本、参考文档等）
skill = SkillParser.load_skill(Path("./skills/my-skill"))
```

### Skill 数据结构

```python
@dataclass
class Skill:
    metadata: SkillMetadata  # 元数据
    instructions: str        # 指令内容
    path: Path              # 目录路径
    scripts: Dict[str, str] # 脚本文件
    references: Dict[str, str]  # 参考文档
    assets: List[Path]      # 资源文件

@dataclass
class SkillMetadata:
    name: str
    description: str
    license: Optional[str]
    version: Optional[str]
    author: Optional[str]
    allowed_tools: Optional[List[str]]
    compatibility: Optional[str]
    metadata: Dict[str, Any]
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
from skill_manager import LLMBackend

class MyCustomBackend(LLMBackend):
    def complete(
        self, 
        messages, 
        system_prompt=None,
        tools=None
    ) -> str:
        # 实现你的 LLM 调用逻辑
        pass
    
    def get_model_name(self) -> str:
        return "my-custom-model"
```

## Skill 规范

### 目录结构

```
my-skill/
├── SKILL.md          # 必需：主文件
├── scripts/          # 可选：可执行脚本
│   ├── helper.py
│   └── setup.sh
├── references/       # 可选：参考文档
│   ├── api.md
│   └── examples.md
└── assets/          # 可选：资源文件
    └── template.json
```

### SKILL.md 格式

```markdown
---
name: my-skill-name          # 必需：小写字母、数字、连字符，最多64字符
description: What this does   # 必需：最多1024字符
license: MIT                  # 可选
metadata:                     # 可选
  author: your-name
  version: "1.0.0"
---

# Skill Instructions

这里是 LLM 会收到的指令内容...
```

### 名称规则

- 最多 64 个字符
- 只能包含小写字母、数字、连字符
- 不能以连字符开头或结尾

## 兼容性

此库创建的 Skills 与以下平台兼容：

| 平台 | 支持情况 |
|------|----------|
| Claude Code | ✅ |
| OpenAI Codex | ✅ |
| GitHub Copilot | ✅ |
| VS Code | ✅ |
| Cursor | ✅ |
| Gemini CLI | ✅ |

## 示例

查看 `examples.py` 获取更多使用示例：

```bash
python examples.py
```

## License

MIT License - 详见 [LICENSE](LICENSE) 文件
## 📞 联系方式

- GitHub Issues: https://github.com/hezuogongying/pay-stack/issues
- Email: 139563281@qq.com

---

<div align="center">

**⭐ 如果这个项目对你有帮助,请给我们一个Star!**

[GitHub](https://github.com/hezuogongying/pay-stack) | [Gitee](https://gitee.com/hezuo_111_admin/pay-stack)

Made with ❤️ by Pay-Stack Team

</div>

---

## 💬 赞赏支持

<div align="center">

微信赞赏码 &nbsp;&nbsp;&nbsp;&nbsp; 支付宝赞助码

<br>

<img width="200" height="200" src="assets/wx_pay.png" style="object-fit: contain;"/>
&nbsp;&nbsp;&nbsp;&nbsp;
<img width="200" height="200" src="assets/hzwy_pay.png" style="object-fit: contain;"/>

</div>

---

## 📢 问题沟通

<div align="center">

加微信群沟通,关注公众号获取最新版本

<br>

微信群 &nbsp;&nbsp;&nbsp;&nbsp; 公众号

<br>

<img width="200" height="200" src="assets/wx_qun.png" style="object-fit: contain;"/>
&nbsp;&nbsp;&nbsp;&nbsp;
<img width="200" height="200" src="assets/gzh_vip.png" style="object-fit: contain;"/>

</div>