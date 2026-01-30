# Zimeiti Skills - 自媒体内容创作技能集

这是一个为自媒体内容创作者设计的 Claude Code Skills 集合，包含 30+ 个专业技能模块，覆盖从选题策划、内容创作、素材采集到文档处理的全流程。

## 📚 目录

- [内容创作类](#内容创作类)
- [素材采集类](#素材采集类)
- [文档处理类](#文档处理类)
- [设计美化类](#设计美化类)
- [开发工具类](#开发工具类)
- [任务管理类](#任务管理类)
- [记忆管理类](#记忆管理类)

---

## 🎨 内容创作类

### AI Writing Assistant (ai-writing-assistant)
**AI写作助手** - 提供6种结构化写作方法，帮助用户创作社交媒体内容。

**核心功能：**
- 对话式创作：通过提问帮助梳理思路
- 大纲式创作：根据大纲扩写文章
- 补充式创作：完成未写完的段落
- 灵感激发：生成选题和写作角度
- 改写优化：提升文章质量
- 素材整合：整合多来源内容

**使用场景：**
- 写社交媒体帖子、文章或内容
- 克服写作障碍
- 构思和提升写作质量
- 整合多个信息源

### Content Rewriting (content-rewriting-2601)
**内容仿写工作流** - 将现有内容进行扩充、改写、优化，融合多种写作风格。

**核心风格：**
- 风格A：个人体验切入型
- 风格B：碎碎念深度思考型
- 风格C：概念提炼实操型
- 风格D：产品体验分享型

**使用场景：**
- 用户提供选题/观点/大纲要求扩写
- 用户提供内容要求改写优化
- 以特定风格重写内容

### Content Topic Generator (content-topic-generator)
**选题生成器** - 从文章、推文、社交媒体内容生成多角度选题。

**四种策略：**
- 延伸策略：在原观点基础上深化
- 反驳策略：提出相反或不同角度观点
- 扩充策略：对某个点进行深度展开
- 热点结合策略：与时事/节日结合

**输出内容：**
- 推文选题（140字完整内容）
- 公众号选题（含详细大纲）

### Content Digest (content-digest)
**内容摘要** - 将长视频、播客、访谈、文章转化为短文和长文叙事。

**核心功能：**
- 短文：300-800字社交媒体摘要，带编号列表
- 长文：1500-3000字叙事文章，有故事弧线

**使用场景：**
- 用户提供YouTube链接、播客文稿、长文章
- 需要摘要、核心洞察或内容重新格式化

### Article Review (article-review)
**文章评价写作** - 根据原文内容撰写深度文章评价/解读。

**写作流程：**
1. 提炼传播点（热点 + 深层价值）
2. 作者背景介绍
3. 核心概念提炼与通俗化
4. 金句引用
5. 画面感表达
6. 升华总结

**使用场景：**
- 对技术文章、行业分析、年终总结进行深度解读
- 提炼文章核心观点并重新表达
- 为社交媒体传播生成二次内容

### Daily AI Brief (daily-ai-brief)
**每日AI简报** - 追踪指定YouTube播客、Twitter/X博主及Newsletter的每日更新。

**追踪内容源：**
- YouTube播客：Latent Space、AI & I、Google DeepMind等
- Twitter/X博主：Andrej Karpathy、Swyx、Greg Isenberg等
- Newsletters：AI Valley、Every、Ben's Bites等

**使用场景：**
- 用户请求"RSS总结"、"日报"、"看看更新"

### Topic Agent (topic-agent)
**选题系统主控Agent** - 协调热点采集、选题生成、选题审核三个环节。

**触发方式：**
- "开始今日选题"：完整流程
- "今日AI热点"：仅采集热点
- "我有一个选题"：单个选题分析
- "推荐一些好的选题"：直接推荐

**输出位置：** Obsidian选题库

### Topic Collector (topic-collector)
**AI热点采集工具** - 从Twitter/X、Product Hunt、Reddit、Hacker News等采集AI热点。

**聚焦领域：**
1. Vibe Coding（自然语言编程、Cursor、Claude Code）
2. Claude生态（Claude Skill、MCP Server）
3. AI Agent（自动化工作流）
4. AI知识管理
5. 模型更新
6. AI新产品
7. 海外热点

### Topic Generator (topic-generator)
**选题生成器** - 根据用户需求和目标生成内容选题。

**使用场景：**
- 需要内容创作灵感
- 需要根据特定主题生成选题

### Topic Reviewer (topic-reviewer)
**选题审核工具** - 对生成的选题进行评估和优化。

**审核维度：**
- 热度（30%）
- 独特角度（40%）
- 国内关注度（30%）

---

## 📥 素材采集类

### Web Scraper (web-scraper)
**网页抓取工具** - 从网页提取内容并转换为干净的Markdown格式。

**使用场景：**
- 用户需要阅读网页文章
- 从URL提取信息
- WebFetch工具因网络限制失败时

### Web Article Translator (web-article-translator)
**文章翻译器** - 翻译在线文章为中文并保存为Markdown格式。

**工作流程：**
1. 使用webReader工具获取文章内容
2. 翻译为中文（保持原文风格）
3. 保存为Markdown文件
4. 保留原文图片链接

**使用场景：**
- "翻译这篇文章 https://example.com/article"
- "把这个URL的文章翻译成中文并保存"

### YouTube Transcript CN (youtube-transcript-cn)
**YouTube字幕提取** - 从YouTube视频提取字幕并转换为中文文字稿。

**功能：**
- 支持自动生成字幕和手动字幕
- 支持简体中文、繁体中文、英文
- 输出格式：text、markdown、json
- 可选时间戳

**使用场景：**
- 用户提供YouTube链接要求提取字幕
- "帮我把这个YouTube视频转成文字"

---

## 📄 文档处理类

### DOCX (docx)
**Word文档处理** - 创建、编辑、分析Word文档。

**核心功能：**
- 创建新文档
- 修改或编辑内容
- 使用追踪更改
- 添加评论
- 文本提取

### PPTX (pptx)
**PowerPoint演示文稿** - 创建、编辑、分析演示文稿。

**工作流程：**
1. 不使用模板：使用html2pptx工作流
2. 使用模板：复制/重新排列模板幻灯片

**设计原则：**
- 根据内容选择合适的颜色和设计元素
- 使用web安全字体
- 创建清晰的视觉层次

### PDF (pdf)
**PDF处理工具包** - 提取文本和表格、创建新PDF、合并/分割文档、处理表单。

**核心库：**
- pypdf：基本操作（合并、分割、旋转）
- pdfplumber：文本和表格提取
- reportlab：创建PDF

### XLSX (xlsx)
**Excel电子表格** - 创建、编辑、分析电子表格，支持公式、格式化、数据分析和可视化。

**核心功能：**
- 创建带公式和格式的新电子表格
- 读取或分析数据
- 修改现有电子表格（保留公式）
- 数据分析和可视化
- 重新计算公式

### Doc Co-authoring (doc-coauthoring)
**文档协作工作流** - 引导用户通过结构化流程协作创建文档。

**三个阶段：**
1. 上下文收集
2. 细化与结构
3. 读者测试

**使用场景：**
- 写文档、创建提案、起草规范
- 写决策文档、RFC

---

## 🎨 设计美化类

### Algorithmic Art (algorithmic-art)
**算法艺术** - 使用p5.js创建算法艺术，具有种子随机性和交互式参数探索。

**创作流程：**
1. 创建算法哲学（.md文件）
2. 用p5.js表达（.html + .js文件）

**关键特性：**
- 种子随机性（可重现）
- 参数化变化
- 控制混沌
- 交互式探索

**使用场景：**
- 用户请求使用代码创建艺术
- 生成艺术、算法艺术、流场、粒子系统

### Canvas Design (canvas-design)
**画布设计** - 创建精美的视觉艺术，输出为.png和.pdf文档。

**创作流程：**
1. 设计哲学创建（.md文件）
2. 在画布上表达（.pdf或.png文件）

**使用场景：**
- 创建海报、艺术品、设计
- 其他静态作品

### Frontend Design (frontend-design)
**前端设计** - 创建独特、生产级的前端界面，具有高设计质量。

**设计思维：**
- 目的：这个界面解决什么问题？
- 风格：选择极端风格（极简、极繁、复古未来等）
- 约束：技术要求
- 差异化：让人难忘的是什么

**使用场景：**
- 构建web组件、页面、工件、海报
- 网站、着陆页、仪表板、React组件

### Brand Guidelines (brand-guidelines)
**品牌指南** - 应用Anthropic官方品牌颜色和字体。

**品牌资源：**
- 主色：深色、浅色、中灰、浅灰
- 强调色：橙色、蓝色、绿色
- 字体：标题用Poppins，正文用Lora

**使用场景：**
- 品牌颜色或风格指南、视觉格式、公司设计标准

### Theme Factory (theme-factory)
**主题工厂** - 用主题为工件添加样式，10个预设主题。

**可用主题：**
1. Ocean Depths - 专业海洋主题
2. Sunset Boulevard - 温暖日落色
3. Forest Canopy - 自然大地色
4. Modern Minimalist - 现代极简
5. Golden Hour - 秋日温暖
6. Arctic Frost - 凉爽冬季
7. Desert Rose - 柔和尘埃色调
8. Tech Innovation - 大胆科技美学
9. Botanical Garden - 清新有机
10. Midnight Galaxy - 戏剧宇宙色调

### Slack GIF Creator (slack-gif-creator)
**Slack GIF创建器** - 创建针对Slack优化的动画GIF。

**Slack要求：**
- Emoji GIF：128x128（推荐）
- 消息GIF：480x480
- FPS：10-30
- 颜色：48-128
- 持续时间：3秒以内

**使用场景：**
- "给我做一个X做Y的Slack GIF"

---

## 🛠 开发工具类

### MCP Builder (mcp-builder)
**MCP服务器开发指南** - 创建高质量的MCP服务器，使LLM能够与外部服务交互。

**支持框架：**
- Python（FastMCP）
- Node/TypeScript（MCP SDK）

**四个阶段：**
1. 深度研究和规划
2. 实现
3. 审查和测试
4. 创建评估

### Skill Creator (skill-creator)
**技能创建指南** - 创建有效的技能，扩展Claude的能力。

**技能结构：**
```
skill-name/
├── SKILL.md (必需)
└── Bundled Resources (可选)
    ├── scripts/     - 可执行代码
    ├── references/  - 文档资料
    └── assets/      - 输出中使用的文件
```

**创建流程：**
1. 用具体示例理解技能
2. 规划可重用内容
3. 初始化技能
4. 编辑技能
5. 打包技能
6. 迭代

### Web Artifacts Builder (web-artifacts-builder)
**Web工件构建器** - 使用现代前端技术创建复杂的多组件HTML工件。

**技术栈：**
- React 18 + TypeScript
- Vite
- Tailwind CSS 3.4.1
- shadcn/ui组件
- Parcel（打包）

**使用场景：**
- 需要状态管理、路由或shadcn/ui组件的复杂工件
- 不是简单的单文件HTML/JSX工件

### Webapp Testing (webapp-testing)
**Web应用测试** - 使用Playwright与本地web应用交互和测试。

**功能：**
- 验证前端功能
- 调试UI行为
- 捕获浏览器截图
- 查看浏览器日志

**辅助脚本：**
- `scripts/with_server.py` - 管理服务器生命周期

---

## 📋 任务管理类

### Task Drill (task-drill)
**AI任务钻头** - 任务拆解助手，指导按任务类型进行任务拆解。

**四种任务类型：**
1. 直接问题解决：快速解决具体问题
2. 直接输出生成：生成较长内容
3. 协作问题解决：通过多轮对话解决复杂问题
4. 协作输出生成：通过多轮对话生成内容

**使用场景：**
- 用户提出任何任务
- 需要帮助制定计划
- 要求拆解工作

### Product Strategy Analyzer (product-strategy-analyzer)
**产品战略分析** - 分析产品创意、评估市场机会、探讨产品可能性。

**分析方法：**
- 倒推法：从终局往回推（5-10年）
- 顺推法：从现状往前推（MVP → 迭代 → 规模化）

**搜索策略：**
- 竞品搜索
- 市场信息
- 案例研究

---

## 🧠 记忆管理类

### Mem Record (mem-record)
**记忆记录** - AI个人记忆系统的记忆记录功能。

**四个记忆层级：**
- L1情境层：日常记录
- L2行为层：习惯与偏好（3次+）
- L3认知层：思维模式
- L4核心层：价值观（只能手动修改）

**使用场景：**
- 用户说"记录到记忆系统"、"记住这个"
- 检测到重要事件、决策、偏好表达
- 用户完成重要任务或做出决策

### Mem File Scan (mem-file-scan)
**文件扫描** - 扫描文件并提取关键信息。

### Mem Monthly (mem-monthly)
**月度记忆** - 月度记忆整理。

### Mem Query (mem-query)
**记忆查询** - 查询记忆系统。

### Mem Weekly (mem-weekly)
**周度记忆** - 周度记忆整理。

---

## 📢 内部沟通类

### Internal Comms (internal-comms)
**内部沟通** - 帮助编写各种内部沟通内容。

**支持类型：**
- 3P更新（Progress、Plans、Problems）
- 公司通讯
- FAQ回答
- 状态报告
- 领导层更新
- 项目更新
- 事故报告

---

## 🚀 快速开始

1. **安装Claude Code** - 确保已安装Claude Code CLI工具
2. **克隆此仓库** - 将skills放置在Claude Code的skills目录
3. **使用技能** - 在对话中自然触发，或直接指定使用

## 📝 许可证

各个技能可能有不同的许可证，请查看具体技能目录中的LICENSE.txt文件。

## 🤝 贡献

欢迎提交问题和改进建议！

---

**最后更新：** 2026年1月29日
