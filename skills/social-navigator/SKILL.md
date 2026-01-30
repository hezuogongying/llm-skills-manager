---
name: social-navigator
description: 基于Agent原理的社交对话引导技能，包含策略层和人格化表达层。当用户需要在特定社交场景中达成目标时使用，如：建立商业合作关系、获取专业建议、拓展人脉、职业机会探索、获取资源帮助等。用户需提供：(1)社交目标 (2)对方角色/职业背景 (3)自己的人设和表达风格。技能将引导用户通过对话逐步收敛路径、探测需求、创造价值、达成目标，并生成符合人设的自然表达，避免AI痕迹。适用于网络聊天、邮件往来、社交媒体互动等文字社交场景。
---

# Social Navigator 社交导航技能

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│  策略层（做什么）                                        │
│  对话文本 → 解析DOM → 选择操作 → 路径收敛               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  表达层（怎么说）                                        │
│  策略意图 → 人格过滤 → 情绪调整 → 平台适配 → 真人化输出  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  持久层（记住什么）                     SQLite 数据库    │
│  会话配置 / 对话历史 / 关键发现 / 对方画像 / 里程碑      │
└─────────────────────────────────────────────────────────┘
```

## 数据库操作

本 Skill 使用 SQLite 持久化存储。数据库文件：`~/social_nav.db`

### 初始化（首次使用）
```bash
python scripts/db_manager.py init
```

### 核心函数调用

```python
from scripts.db_manager import (
    # 智能初始化
    smart_session_init,       # 根据名称+目标查找或创建会话
    get_init_questions,       # 获取初始化问题列表
    create_session_from_answers,  # 从问答结果创建会话
    find_session,             # 查找匹配的会话
    
    # 会话管理
    create_session,           # 创建新会话（完整配置）
    get_session,              # 获取会话完整数据
    get_session_summary,      # 获取会话摘要（用于恢复上下文）
    list_sessions,            # 列出所有会话
    close_session,            # 关闭会话
    export_session,           # 导出会话为JSON
    
    # 对话记录
    add_conversation,         # 记录一轮对话
    add_discovery,            # 添加关键发现
    update_target_profile,    # 更新对方画像
    add_milestone,            # 添加里程碑
)
```

## 使用流程

### 0. 会话入口：智能初始化

每次用户开启社交导航时，首先询问两个核心问题：

```
Claude: "对方的名称是什么？（人名/昵称/公司名都可以）"
用户: "李总"

Claude: "你想达成什么目标？"
用户: "建立商务合作"
```

然后调用智能初始化：

```python
from scripts.db_manager import smart_session_init

result = smart_session_init(target_name='李总', goal='商务合作')

if result['action'] == 'resume':
    # 找到已有会话，直接恢复
    print(f"找到之前的会话：{result['message']}")
    session = result['session']
    # 跳过初始化问题，直接进入导航

elif result['action'] == 'select':
    # 找到多个匹配，让用户选择
    print("找到多个相关会话，请选择：")
    for s in result['candidates']:
        print(f"  [{s['id']}] {s['name']} - {s['goal']}")
    # 用户选择后恢复

elif result['action'] == 'create':
    # 没找到，需要收集更多信息创建新会话
    print("这是新的社交目标，需要补充一些信息...")
    # 进入完整初始化流程
```

### 1. 新会话：渐进式信息收集

如果是新会话，**逐步询问**以下信息（用户可跳过非必填项）：

```python
from scripts.db_manager import get_init_questions, create_session_from_answers

questions = get_init_questions()
# 返回:
# - target_name (必填): 对方的名称是什么？
# - goal (必填): 你想达成什么目标？
# - target_role (可选): 对方是什么角色/职位？
# - target_company (可选): 对方所在的公司/组织？
# - relationship_start (可选): 你们目前是什么关系？默认"弱关系"
# - channel (可选): 通过什么渠道沟通？默认"微信"
# - persona_age (可选): 你的年龄段？默认"20s"
# - persona_personality (可选): 你的性格倾向？
# - persona_phrases (可选): 你常用的口癖/词汇？默认"好的,明白,哈哈"
```

收集完成后创建会话：

```python
session_id = create_session_from_answers({
    'target_name': '李总',
    'goal': '建立商务合作',
    'target_role': '采购总监',
    'target_company': 'ABC公司',
    # 其他用户回答的字段...
    # 未回答的使用默认值
})
```

### 2. 继续会话：恢复上下文

```python
from scripts.db_manager import get_session_summary

# 获取摘要恢复记忆
summary = get_session_summary(session_id)
print(summary)  # 包含配置、历史、关键发现
```

### 3. 每轮对话：分析并记录

```python
# 记录本轮对话和分析结果
add_conversation(session_id, {
    'their_message': '对方的消息内容',
    'emotional_state': '中性偏积极',
    'explicit_needs': '对方明确表达的需求',
    'implicit_clues': '推断出的线索',
    'actionable_nodes': [
        {'content': '节点1', 'operation': '共情确认'},
        {'content': '节点2', 'operation': '开放提问'}
    ],
    'risk_signals': '如有风险信号',
    'chosen_operation': '价值提供',
    'operation_purpose': '展示匹配度',
    'strategic_intent': '推动进入下一阶段',
    'my_response': '生成的回复内容',
    'current_stage': '信息收集',
    'distance_to_goal': '中',
    'path_convergence': '逐渐清晰',
    'relationship_temperature': '温'
})

# 如果发现关键信息，单独记录
add_discovery(session_id, 
    content='对方团队正在扩招',
    category='opportunity',  # need/pain/concern/decision/timeline/number/competition/opportunity/other
    importance='high',       # critical/high/normal/low
    source_round=1
)
```

### 4. 更新对方画像

```python
update_target_profile(session_id, {
    'communication_style': '简洁直接',
    'decision_mode': '需要请示上级',
    'concerns': ['候选人稳定性', '技术匹配度'],
    'taboos': ['不要催促'],
    'preferences': ['喜欢有准备的人'],
    'observed_traits': ['回复快', '愿意帮忙']
})
```

### 5. 记录里程碑

```python
add_milestone(session_id,
    title='对方同意内推',
    description='明确表示会推荐简历给HR',
    milestone_type='positive',  # positive/negative/neutral
    round_number=5
)
```

### 6. 结束会话

```python
close_session(session_id, outcome='completed')  # completed/abandoned/on_hold
export_session(session_id)  # 可选：导出为JSON备份
```

## 执行循环

每轮对话执行以下流程：

```
┌─ 1. 恢复上下文 ────────────────────────┐
│ get_session_summary(session_id)       │
│ → 获取配置、历史、关键发现             │
└───────────────────────────────────────┘
        ↓
┌─ 2. 获取输入 ─────────────────────────┐
│ 用户粘贴对方的最新消息                 │
└───────────────────────────────────────┘
        ↓
┌─ 3. 解析对话DOM ─────────────────────┐
│ - 情感状态（积极/中性/防备/负面）      │
│ - 显性需求（对方明确表达的）           │
│ - 隐性线索（可推断的潜在需求）         │
│ - 可操作节点（可回应/可深挖的点）      │
│ - 风险信号（敷衍/拒绝/不耐烦）         │
└───────────────────────────────────────┘
        ↓
┌─ 4. 路径评估 ────────────────────────┐
│ - 当前阶段：建立连接→信息收集→价值交换→目标推进→收尾
│ - 距离目标：远/中/近                   │
│ - 路径收敛度：模糊→逐渐清晰→清晰       │
└───────────────────────────────────────┘
        ↓
┌─ 5. 策略决策 ────────────────────────┐
│ 选择最优社交操作（见下方工具集）        │
└───────────────────────────────────────┘
        ↓
┌─ 6. 人格化表达 ──────────────────────┐
│ 策略意图 → 人格过滤 → 情绪调整 → 去AI化 │
│ （详见 references/persona.md）        │
└───────────────────────────────────────┘
        ↓
┌─ 7. 持久化 ──────────────────────────┐
│ add_conversation() 记录本轮            │
│ add_discovery() 记录关键发现（如有）    │
│ update_target_profile() 更新画像（如有）│
│ add_milestone() 记录里程碑（如有）      │
└───────────────────────────────────────┘
```

## 社交操作工具集

| 操作类型 | 用途 | 时机 |
|---------|------|------|
| **共情确认** | 建立信任和连接 | 对方表达情绪/困难时 |
| **开放提问** | 展开更多信息节点 | 信息不足，需要探测 |
| **封闭提问** | 确认特定属性 | 需要验证假设 |
| **复述确认** | 验证理解是否正确 | 关键信息需确认 |
| **价值提供** | 创造互惠基础 | 已识别对方需求 |
| **轻推试探** | 测试对方意愿 | 路径接近目标时 |
| **锚定退让** | 从高位谈判 | 正式提议阶段 |
| **沉默留白** | 给对方表达空间 | 对方需要思考时 |
| **自我暴露** | 触发对等分享 | 需要对方打开 |
| **战略撤退** | 保留关系等待时机 | 遇到明确拒绝 |

## 输出格式

每次分析后输出：

```
## 对话DOM解析

**情感状态**: [积极/中性/防备/负面] + 具体依据
**显性需求**: [对方明确说的]
**隐性线索**: [可推断的]
**可操作节点**: 
  - 节点1: [具体内容] → 可用操作: [操作类型]
  - 节点2: [具体内容] → 可用操作: [操作类型]
**风险信号**: [如有]

## 路径评估

**距离目标**: [远/中/近/已达成]
**路径收敛度**: [模糊/逐渐清晰/清晰/完全确定]
**当前阶段**: [建立连接/信息收集/价值交换/目标推进/收尾确认]

## 策略层决策

**核心操作**: [选择的操作类型]
**操作目的**: [这一步要达成什么]
**策略意图**: [想传达的核心信息]

## 表达层处理

**情绪适配**: [当前应表现的情绪状态]
**风格检查**: [确认符合人设]
**AI痕迹检查**: [排除机器感表达]

## 最终话术

[经过人格化处理的回复，可能拆分为多条消息]

---
*提示：发送后请粘贴对方的回复，继续导航*
```

## 关键原则

### 策略层原则
1. **路径收敛优先**：每一步都应让目标更清晰，不做无效社交
2. **价值先行**：先创造价值，再寻求回报
3. **探测而非假设**：不确定时用提问验证，不要自己脑补
4. **保护关系**：遇阻时保留关系，不强推硬谈
5. **节奏控制**：不要一次性推进太多，给对方消化空间

### 表达层原则
1. **人格一致性**：始终保持同一个人设的表达风格
2. **情绪真实性**：情绪表达要符合情境，不要永远"积极热情"
3. **适度不完美**：真人会有错别字、口语化、不完整句子
4. **平台适配**：微信碎片化、邮件正式化、LinkedIn专业化
5. **避免AI特征**：不用"首先其次"、不过度礼貌、不信息过载

## 参考文档

- 场景模板和解析示例：`references/scenarios.md`
- 人格化表达系统：`references/persona.md`
