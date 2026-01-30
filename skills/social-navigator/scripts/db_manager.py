#!/usr/bin/env python3
"""
Social Navigator - SQLite 持久化管理
用于存储和检索社交导航会话状态
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

# 默认数据库路径
DEFAULT_DB_PATH = os.path.expanduser("~/social_nav.db")


def get_db_path(custom_path=None):
    """获取数据库路径"""
    return custom_path or DEFAULT_DB_PATH


def init_db(db_path=None):
    """初始化数据库，创建所有必要的表"""
    db_path = get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 会话配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            
            -- 目标配置
            goal TEXT NOT NULL,
            success_criteria TEXT,
            
            -- 对方信息
            target_role TEXT,
            target_company TEXT,
            target_background TEXT,
            relationship_start TEXT,
            
            -- 我的人设
            persona_age TEXT,
            persona_gender TEXT,
            persona_personality TEXT,
            persona_social_style TEXT,
            persona_background TEXT,
            persona_phrases TEXT,  -- JSON array
            persona_emoji_usage TEXT,
            persona_message_length TEXT,
            
            -- 沟通渠道
            channel TEXT,
            
            -- 当前状态
            current_stage TEXT DEFAULT '建立连接',
            distance_to_goal TEXT DEFAULT '远',
            path_convergence TEXT DEFAULT '模糊',
            relationship_temperature TEXT DEFAULT '温'
        )
    ''')
    
    # 对话记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            round_number INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- 对方消息
            their_message TEXT,
            
            -- DOM解析结果
            emotional_state TEXT,
            explicit_needs TEXT,
            implicit_clues TEXT,
            actionable_nodes TEXT,  -- JSON
            risk_signals TEXT,
            
            -- 策略决策
            chosen_operation TEXT,
            operation_purpose TEXT,
            strategic_intent TEXT,
            
            -- 我的回复
            my_response TEXT,
            
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    # 关键发现表（累积，不会丢失）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discoveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT,  -- need/pain/concern/decision/timeline/number/competition/other
            content TEXT NOT NULL,
            source_round INTEGER,
            importance TEXT DEFAULT 'normal',  -- critical/high/normal/low
            
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    # 对方画像表（持续更新）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS target_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            communication_style TEXT,
            decision_mode TEXT,
            concerns TEXT,  -- JSON array
            taboos TEXT,  -- JSON array
            preferences TEXT,  -- JSON array
            observed_traits TEXT,  -- JSON array
            
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    # 里程碑表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            round_number INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            milestone_type TEXT,  -- positive/negative/neutral
            
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {db_path}")
    return db_path


def create_session(config, db_path=None):
    """创建新的社交导航会话"""
    db_path = get_db_path(db_path)
    init_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (
            name, goal, success_criteria,
            target_role, target_company, target_background, relationship_start,
            persona_age, persona_gender, persona_personality, persona_social_style,
            persona_background, persona_phrases, persona_emoji_usage, persona_message_length,
            channel
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        config.get('name', f"会话_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
        config['goal'],
        config.get('success_criteria', ''),
        config.get('target_role', ''),
        config.get('target_company', ''),
        config.get('target_background', ''),
        config.get('relationship_start', '陌生'),
        config.get('persona_age', ''),
        config.get('persona_gender', ''),
        config.get('persona_personality', ''),
        config.get('persona_social_style', ''),
        config.get('persona_background', ''),
        json.dumps(config.get('persona_phrases', []), ensure_ascii=False),
        config.get('persona_emoji_usage', ''),
        config.get('persona_message_length', ''),
        config.get('channel', '微信')
    ))
    
    session_id = cursor.lastrowid
    
    # 初始化对方画像
    cursor.execute('''
        INSERT INTO target_profile (session_id) VALUES (?)
    ''', (session_id,))
    
    conn.commit()
    conn.close()
    
    print(f"创建会话成功，ID: {session_id}")
    return session_id


def get_session(session_id, db_path=None):
    """获取会话完整信息"""
    db_path = get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取会话基本信息
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = dict(cursor.fetchone() or {})
    
    if not session:
        conn.close()
        return None
    
    # 解析JSON字段
    if session.get('persona_phrases'):
        session['persona_phrases'] = json.loads(session['persona_phrases'])
    
    # 获取最近5轮对话
    cursor.execute('''
        SELECT * FROM conversations 
        WHERE session_id = ? 
        ORDER BY round_number DESC 
        LIMIT 5
    ''', (session_id,))
    session['recent_conversations'] = [dict(row) for row in cursor.fetchall()][::-1]
    
    # 获取所有关键发现
    cursor.execute('''
        SELECT * FROM discoveries 
        WHERE session_id = ? 
        ORDER BY timestamp ASC
    ''', (session_id,))
    session['discoveries'] = [dict(row) for row in cursor.fetchall()]
    
    # 获取对方画像
    cursor.execute('''
        SELECT * FROM target_profile 
        WHERE session_id = ? 
        ORDER BY updated_at DESC 
        LIMIT 1
    ''', (session_id,))
    profile = cursor.fetchone()
    if profile:
        profile = dict(profile)
        for field in ['concerns', 'taboos', 'preferences', 'observed_traits']:
            if profile.get(field):
                profile[field] = json.loads(profile[field])
        session['target_profile'] = profile
    
    # 获取里程碑
    cursor.execute('''
        SELECT * FROM milestones 
        WHERE session_id = ? 
        ORDER BY timestamp ASC
    ''', (session_id,))
    session['milestones'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return session


def add_conversation(session_id, data, db_path=None):
    """添加一轮对话记录"""
    db_path = get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取当前轮次
    cursor.execute('''
        SELECT COALESCE(MAX(round_number), 0) + 1 
        FROM conversations 
        WHERE session_id = ?
    ''', (session_id,))
    round_number = cursor.fetchone()[0]
    
    cursor.execute('''
        INSERT INTO conversations (
            session_id, round_number,
            their_message, emotional_state, explicit_needs, implicit_clues,
            actionable_nodes, risk_signals,
            chosen_operation, operation_purpose, strategic_intent,
            my_response
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        session_id, round_number,
        data.get('their_message', ''),
        data.get('emotional_state', ''),
        data.get('explicit_needs', ''),
        data.get('implicit_clues', ''),
        json.dumps(data.get('actionable_nodes', []), ensure_ascii=False),
        data.get('risk_signals', ''),
        data.get('chosen_operation', ''),
        data.get('operation_purpose', ''),
        data.get('strategic_intent', ''),
        data.get('my_response', '')
    ))
    
    # 更新会话时间和状态
    cursor.execute('''
        UPDATE sessions SET 
            updated_at = CURRENT_TIMESTAMP,
            current_stage = COALESCE(?, current_stage),
            distance_to_goal = COALESCE(?, distance_to_goal),
            path_convergence = COALESCE(?, path_convergence),
            relationship_temperature = COALESCE(?, relationship_temperature)
        WHERE id = ?
    ''', (
        data.get('current_stage'),
        data.get('distance_to_goal'),
        data.get('path_convergence'),
        data.get('relationship_temperature'),
        session_id
    ))
    
    conn.commit()
    conn.close()
    
    print(f"记录第 {round_number} 轮对话")
    return round_number


def add_discovery(session_id, content, category='other', importance='normal', source_round=None, db_path=None):
    """添加关键发现"""
    db_path = get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO discoveries (session_id, category, content, importance, source_round)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, category, content, importance, source_round))
    
    conn.commit()
    conn.close()
    print(f"添加关键发现: [{category}] {content[:50]}...")


def update_target_profile(session_id, profile_data, db_path=None):
    """更新对方画像"""
    db_path = get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 处理JSON字段
    for field in ['concerns', 'taboos', 'preferences', 'observed_traits']:
        if field in profile_data and isinstance(profile_data[field], list):
            profile_data[field] = json.dumps(profile_data[field], ensure_ascii=False)
    
    cursor.execute('''
        INSERT INTO target_profile (
            session_id, communication_style, decision_mode,
            concerns, taboos, preferences, observed_traits
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        session_id,
        profile_data.get('communication_style', ''),
        profile_data.get('decision_mode', ''),
        profile_data.get('concerns', '[]'),
        profile_data.get('taboos', '[]'),
        profile_data.get('preferences', '[]'),
        profile_data.get('observed_traits', '[]')
    ))
    
    conn.commit()
    conn.close()
    print("更新对方画像")


def add_milestone(session_id, title, description='', milestone_type='neutral', round_number=None, db_path=None):
    """添加里程碑"""
    db_path = get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO milestones (session_id, title, description, milestone_type, round_number)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, title, description, milestone_type, round_number))
    
    conn.commit()
    conn.close()
    print(f"添加里程碑: {title}")


def list_sessions(db_path=None, status='active'):
    """列出所有会话"""
    db_path = get_db_path(db_path)
    if not os.path.exists(db_path):
        print("数据库不存在")
        return []
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if status:
        cursor.execute('''
            SELECT id, name, goal, current_stage, distance_to_goal, 
                   created_at, updated_at, status
            FROM sessions 
            WHERE status = ?
            ORDER BY updated_at DESC
        ''', (status,))
    else:
        cursor.execute('''
            SELECT id, name, goal, current_stage, distance_to_goal,
                   created_at, updated_at, status
            FROM sessions 
            ORDER BY updated_at DESC
        ''')
    
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return sessions


def get_session_summary(session_id, db_path=None):
    """获取会话摘要（用于恢复上下文）"""
    session = get_session(session_id, db_path)
    if not session:
        return None
    
    summary = f"""
## 会话状态摘要

### 基础配置
- **目标**: {session['goal']}
- **对方**: {session['target_role']} @ {session['target_company']}
- **渠道**: {session['channel']}

### 我的人设
- 年龄: {session['persona_age']}
- 性格: {session['persona_personality']}
- 风格: {session['persona_social_style']}
- 口癖: {', '.join(session.get('persona_phrases', []))}

### 当前进度
- **阶段**: {session['current_stage']}
- **距离目标**: {session['distance_to_goal']}
- **路径收敛度**: {session['path_convergence']}
- **关系温度**: {session['relationship_temperature']}

### 关键发现 ({len(session.get('discoveries', []))} 条)
"""
    for d in session.get('discoveries', [])[-5:]:  # 最近5条
        summary += f"- [{d['category']}] {d['content']}\n"
    
    summary += f"""
### 最近对话 ({len(session.get('recent_conversations', []))} 轮)
"""
    for conv in session.get('recent_conversations', []):
        summary += f"""
**第{conv['round_number']}轮**
- 对方: {conv['their_message'][:100]}{'...' if len(conv.get('their_message', '')) > 100 else ''}
- 我方策略: {conv['chosen_operation']}
- 我的回复: {conv['my_response'][:100]}{'...' if len(conv.get('my_response', '')) > 100 else ''}
"""
    
    if session.get('milestones'):
        summary += "\n### 里程碑\n"
        for m in session['milestones']:
            summary += f"- [{m['milestone_type']}] {m['title']}\n"
    
    return summary


def close_session(session_id, outcome='completed', db_path=None):
    """关闭会话"""
    db_path = get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE sessions SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (outcome, session_id))
    
    conn.commit()
    conn.close()
    print(f"会话 {session_id} 已关闭，状态: {outcome}")


def export_session(session_id, output_path=None, db_path=None):
    """导出会话为JSON文件"""
    session = get_session(session_id, db_path)
    if not session:
        print(f"会话 {session_id} 不存在")
        return None
    
    output_path = output_path or f"social_nav_session_{session_id}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(session, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"导出完成: {output_path}")
    return output_path


def find_session(target_name=None, goal=None, db_path=None):
    """
    根据对方名称和/或目标查找已有会话
    返回匹配的会话列表，按更新时间倒序
    """
    db_path = get_db_path(db_path)
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    conditions = ["status = 'active'"]
    params = []
    
    if target_name:
        # 模糊匹配对方名称（在 name 或 target_company 或 target_role 中搜索）
        conditions.append("(name LIKE ? OR target_company LIKE ? OR target_role LIKE ?)")
        pattern = f"%{target_name}%"
        params.extend([pattern, pattern, pattern])
    
    if goal:
        conditions.append("goal LIKE ?")
        params.append(f"%{goal}%")
    
    query = f'''
        SELECT id, name, goal, target_role, target_company, 
               current_stage, distance_to_goal, updated_at
        FROM sessions 
        WHERE {' AND '.join(conditions)}
        ORDER BY updated_at DESC
    '''
    
    cursor.execute(query, params)
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return sessions


def smart_session_init(target_name, goal=None, db_path=None):
    """
    智能会话初始化：
    1. 根据 target_name 和 goal 查找已有会话
    2. 如果找到匹配的活跃会话，返回该会话信息
    3. 如果没找到，返回 None（需要创建新会话）
    
    返回: {
        'action': 'resume' | 'create',
        'session': session_data | None,
        'candidates': [matching_sessions] | []
    }
    """
    db_path = get_db_path(db_path)
    init_db(db_path)  # 确保数据库存在
    
    # 查找匹配的会话
    candidates = find_session(target_name, goal, db_path)
    
    if not candidates:
        return {
            'action': 'create',
            'session': None,
            'candidates': [],
            'message': f'未找到与「{target_name}」相关的会话，需要创建新会话'
        }
    
    if len(candidates) == 1:
        # 只有一个匹配，直接恢复
        session = get_session(candidates[0]['id'], db_path)
        return {
            'action': 'resume',
            'session': session,
            'candidates': candidates,
            'message': f'找到会话「{candidates[0]["name"]}」，目标: {candidates[0]["goal"]}'
        }
    
    # 多个匹配，返回候选列表让用户选择
    return {
        'action': 'select',
        'session': None,
        'candidates': candidates,
        'message': f'找到 {len(candidates)} 个相关会话，请选择'
    }


def get_init_questions():
    """
    返回初始化会话需要收集的问题列表
    每个问题包含: key, question, required, default, hint
    """
    return [
        {
            'key': 'target_name',
            'question': '对方的名称是什么？',
            'hint': '可以是人名、昵称、公司名，用于识别和查找历史会话',
            'required': True,
            'default': None
        },
        {
            'key': 'goal',
            'question': '你想达成什么目标？',
            'hint': '例如：获得内推机会、建立合作、获取建议',
            'required': True,
            'default': None
        },
        {
            'key': 'target_role',
            'question': '对方是什么角色/职位？',
            'hint': '例如：资深工程师、产品总监、创业者',
            'required': False,
            'default': ''
        },
        {
            'key': 'target_company',
            'question': '对方所在的公司/组织？',
            'hint': '可以跳过',
            'required': False,
            'default': ''
        },
        {
            'key': 'relationship_start',
            'question': '你们目前是什么关系？',
            'hint': '陌生人 / 弱关系 / 有过接触',
            'required': False,
            'default': '弱关系'
        },
        {
            'key': 'channel',
            'question': '通过什么渠道沟通？',
            'hint': '微信 / 钉钉 / 邮件 / LinkedIn',
            'required': False,
            'default': '微信'
        },
        {
            'key': 'persona_age',
            'question': '你的年龄段？',
            'hint': '20s / 30s / 40s+，用于匹配表达风格',
            'required': False,
            'default': '20s'
        },
        {
            'key': 'persona_personality',
            'question': '你的性格倾向？',
            'hint': '例如：内敛稳重 / 外向热情 / 理性直接',
            'required': False,
            'default': ''
        },
        {
            'key': 'persona_phrases',
            'question': '你常用的口癖/词汇？',
            'hint': '例如：好的、哈哈、了解，用逗号分隔',
            'required': False,
            'default': '好的,明白,哈哈'
        }
    ]


def create_session_from_answers(answers, db_path=None):
    """
    根据问答结果创建会话
    answers: dict，key 对应 get_init_questions 中的 key
    """
    # 处理口癖字段（字符串转列表）
    phrases = answers.get('persona_phrases', '')
    if isinstance(phrases, str):
        phrases = [p.strip() for p in phrases.split(',') if p.strip()]
    
    config = {
        'name': f"{answers.get('target_name', '未知')} - {answers.get('goal', '未设目标')[:20]}",
        'goal': answers.get('goal', ''),
        'target_role': answers.get('target_role', ''),
        'target_company': answers.get('target_company', ''),
        'target_background': answers.get('target_background', ''),
        'relationship_start': answers.get('relationship_start', '弱关系'),
        'persona_age': answers.get('persona_age', ''),
        'persona_gender': answers.get('persona_gender', ''),
        'persona_personality': answers.get('persona_personality', ''),
        'persona_social_style': answers.get('persona_social_style', ''),
        'persona_background': answers.get('persona_background', ''),
        'persona_phrases': phrases,
        'persona_emoji_usage': answers.get('persona_emoji_usage', '偶尔'),
        'persona_message_length': answers.get('persona_message_length', '中等'),
        'channel': answers.get('channel', '微信')
    }
    
    return create_session(config, db_path)


def format_session_list(sessions):
    """格式化会话列表为可读字符串"""
    if not sessions:
        return "没有找到相关会话"
    
    lines = []
    for i, s in enumerate(sessions, 1):
        lines.append(f"{i}. [{s['id']}] {s['name']}")
        lines.append(f"   目标: {s['goal']}")
        lines.append(f"   阶段: {s['current_stage']} | 距离目标: {s['distance_to_goal']}")
        lines.append(f"   更新: {s['updated_at']}")
        lines.append("")
    
    return '\n'.join(lines)


# CLI 接口
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("""
Social Navigator 数据库管理工具

用法:
  python db_manager.py init                        # 初始化数据库
  python db_manager.py list                        # 列出所有会话
  python db_manager.py find <name> [goal]          # 查找会话
  python db_manager.py smart <name> [goal]         # 智能初始化（查找或创建）
  python db_manager.py get <session_id>            # 获取会话详情
  python db_manager.py summary <session_id>        # 获取会话摘要
  python db_manager.py export <session_id>         # 导出会话为JSON
  python db_manager.py questions                   # 显示初始化问题列表
        """)
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
    elif command == 'list':
        sessions = list_sessions()
        print(format_session_list(sessions))
    elif command == 'find':
        target_name = sys.argv[2] if len(sys.argv) > 2 else None
        goal = sys.argv[3] if len(sys.argv) > 3 else None
        sessions = find_session(target_name, goal)
        print(format_session_list(sessions))
    elif command == 'smart':
        target_name = sys.argv[2] if len(sys.argv) > 2 else ''
        goal = sys.argv[3] if len(sys.argv) > 3 else None
        result = smart_session_init(target_name, goal)
        print(f"Action: {result['action']}")
        print(f"Message: {result['message']}")
        if result['candidates']:
            print("\n候选会话:")
            print(format_session_list(result['candidates']))
    elif command == 'get' and len(sys.argv) > 2:
        session = get_session(int(sys.argv[2]))
        print(json.dumps(session, ensure_ascii=False, indent=2, default=str))
    elif command == 'summary' and len(sys.argv) > 2:
        print(get_session_summary(int(sys.argv[2])))
    elif command == 'export' and len(sys.argv) > 2:
        export_session(int(sys.argv[2]))
    elif command == 'questions':
        questions = get_init_questions()
        for q in questions:
            required = '必填' if q['required'] else '可选'
            default = f"默认: {q['default']}" if q['default'] else ''
            print(f"[{q['key']}] ({required}) {q['question']}")
            print(f"  提示: {q['hint']} {default}")
            print()
    else:
        print("未知命令或参数不足")
