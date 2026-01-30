"""
LLM Skills Manager - Streamlit Web 应用

支持 Skill CRUD 和用户会话交互
"""
import streamlit as st
from pathlib import Path
import tempfile
import shutil

from skill_manager import (
    SkillManager,
    OpenAIBackend,
    AnthropicBackend,
    GoogleBackend,
    OllamaBackend,
    create_skill_template,
    validate_skill,
    MessageRole,
    setup_logging,
)

# 配置日志
setup_logging(level="INFO", use_colors=True)

# 页面配置
st.set_page_config(
    page_title="LLM Skills Manager",
    page_icon="🤖",
    layout="wide",
)

# 初始化会话状态
if "manager" not in st.session_state:
    st.session_state.manager = SkillManager(auto_load=False)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_backend" not in st.session_state:
    st.session_state.current_backend = "Ollama"

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


def get_backend(backend_name: str, model: str = None):
    """获取后端实例"""
    if backend_name == "OpenAI":
        model = model or st.session_state.get("openai_model", "gpt-4o")
        api_key = st.session_state.get("openai_api_key")
        return OpenAIBackend(model=model)
    elif backend_name == "Anthropic":
        model = model or st.session_state.get("anthropic_model", "claude-sonnet-4-20250514")
        return AnthropicBackend(model=model)
    elif backend_name == "Google":
        model = model or st.session_state.get("google_model", "gemini-2.0-flash")
        return GoogleBackend(model=model)
    else:  # Ollama
        model = model or st.session_state.get("ollama_model", "llama3.2")
        base_url = st.session_state.get("ollama_base_url", "http://localhost:11434")
        return OllamaBackend(model=model, base_url=base_url)


# ============================================================================
# 侧边栏 - 配置
# ============================================================================
with st.sidebar:
    st.title("🤖 LLM Skills Manager")

    st.divider()

    # 后端选择
    st.subheader("LLM 后端配置")
    backend_option = st.selectbox(
        "选择后端",
        ["Ollama", "OpenAI", "Anthropic", "Google"],
        index=0,
    )

    if backend_option == "Ollama":
        st.session_state.ollama_model = st.text_input("模型", value="llama3.2")
        st.session_state.ollama_base_url = st.text_input("Base URL", value="http://localhost:11434")
    elif backend_option == "OpenAI":
        st.session_state.openai_api_key = st.text_input("API Key", type="password")
        st.session_state.openai_model = st.selectbox("模型", ["gpt-4o", "gpt-4-turbo", "g-3.5-turbo"])
    elif backend_option == "Anthropic":
        st.session_state.anthropic_api_key = st.text_input("API Key", type="password")
        st.session_state.anthropic_model = st.selectbox("模型", ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022"])
    elif backend_option == "Google":
        st.session_state.google_api_key = st.text_input("API Key", type="password")
        st.session_state.google_model = st.selectbox("模型", ["gemini-2.0-flash", "gemini-1.5-pro"])

    st.session_state.current_backend = backend_option

    st.divider()

    # 页面导航
    st.subheader("导航")
    page = st.radio(
        "选择页面",
        ["💬 聊天", "📚 Skills 管理", "⚙️ 设置"],
    )

    st.divider()

    # Skills 统计
    skills_count = len(st.session_state.manager.list_skills())
    st.metric("已加载 Skills", skills_count)


# ============================================================================
# 聊天页面
# ============================================================================
if page == "💬 聊天":
    st.title("💬 聊天对话")

    # 技能选择
    skills = st.session_state.manager.list_skills()
    if skills:
        skill_names = ["自动匹配"] + [s.name for s in skills]
        selected_skill = st.selectbox("选择 Skill", skill_names)
    else:
        st.info("没有可用的 Skills，请先在 Skills 管理页面添加。")
        selected_skill = None

    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用户输入
    if prompt := st.chat_input("输入您的消息..."):
        # 显示用户消息
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 获取后端
        try:
            backend = get_backend(st.session_state.current_backend)

            # 确定使用的 Skill
            skill_name = None if selected_skill == "自动匹配" else selected_skill

            # 执行
            with st.chat_message("assistant"):
                with st.spinner("思考中..."):
                    response = st.session_state.manager.execute(
                        user_input=prompt,
                        backend=backend,
                        auto_match=(skill_name is None),
                        skill_name=skill_name,
                        conversation_history=st.session_state.conversation_history,
                    )
                    st.markdown(response)

            # 保存响应
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.conversation_history.append(
                {"role": "user", "content": prompt}
            )
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": response}
            )

        except Exception as e:
            st.error(f"发生错误: {e}")

    # 清空对话按钮
    if st.button("清空对话"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()


# ============================================================================
# Skills 管理页面
# ============================================================================
elif page == "📚 Skills 管理":
    st.title("📚 Skills 管理")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("已加载的 Skills")

        skills = st.session_state.manager.list_skills()

        if not skills:
            st.info("没有已加载的 Skills")
        else:
            for skill_meta in skills:
                with st.expander(f"📄 {skill_meta.name}"):
                    st.write(f"**描述**: {skill_meta.description}")
                    if skill_meta.version:
                        st.write(f"**版本**: {skill_meta.version}")
                    if skill_meta.author:
                        st.write(f"**作者**: {skill_meta.author}")

                    # 删除按钮
                    if st.button(f"删除", key=f"delete_{skill_meta.name}"):
                        st.session_state.manager._skills.pop(skill_meta.name, None)
                        st.rerun()

    with col2:
        st.subheader("操作")

        # 加载 Skills
        if st.button("🔄 重新加载默认目录"):
            st.session_state.manager.load_default_skills()
            st.rerun()

        if st.button("📁 从目录加载"):
            dir_path = st.text_input("目录路径", value="./skills")
            if st.button("加载", key="load_from_dir"):
                try:
                    st.session_state.manager.load_skills_from_directory(dir_path)
                    st.success(f"已从 {dir_path} 加载 Skills")
                    st.rerun()
                except Exception as e:
                    st.error(f"加载失败: {e}")

        st.divider()

        # 创建新 Skill
        st.subheader("创建新 Skill")
        new_skill_name = st.text_input("名称 (小写字母、数字、连字符)")
        new_skill_desc = st.text_input("描述")
        new_skill_output = st.text_input("输出目录", value="./skills")

        if st.button("➕ 创建 Skill"):
            if not new_skill_name or not new_skill_desc:
                st.warning("请填写名称和描述")
            else:
                try:
                    skill_dir = create_skill_template(
                        output_dir=new_skill_output,
                        name=new_skill_name,
                        description=new_skill_desc,
                    )
                    st.success(f"已创建 Skill: {skill_dir}")
                    # 自动加载
                    st.session_state.manager.load_skill(skill_dir)
                    st.rerun()
                except Exception as e:
                    st.error(f"创建失败: {e}")

        st.divider()

        # 验证 Skill
        st.subheader("验证 Skill")
        validate_path = st.text_input("Skill 目录路径")

        if st.button("✅ 验证", key="validate_skill"):
            is_valid, errors = validate_skill(validate_path)
            if is_valid:
                st.success("Skill 验证通过！")
            else:
                st.error("验证失败:")
                for error in errors:
                    st.write(f"- {error}")


# ============================================================================
# 设置页面
# ============================================================================
elif page == "⚙️ 设置":
    st.title("⚙️ 设置")

    st.subheader("默认 Skill 目录")

    st.info(
        f"""当前搜索目录:
- `skills/`
- `.claude/skills/`

这些目录会在启动时自动扫描。"""
    )

    st.divider()

    st.subheader("环境变量")

    st.code(
        """# OpenAI
OPENAI_API_KEY=sk-your-api-key

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-api-key

# Google Gemini
GOOGLE_API_KEY=your-api-key

# Ollama (本地)
# OLLAMA_BASE_URL=http://localhost:11434
""",
        language="bash",
    )

    st.divider()

    st.subheader("关于")

    st.info(
        """**LLM Skills Manager v2.0**

遵循 SOLID 原则设计的 Python 库，用于解析和调用 Agent Skills。

支持多种 LLM 后端：
- OpenAI (GPT-4, GPT-4o)
- Anthropic Claude
- Google Gemini
- Ollama (本地模型)

GitHub: https://github.com/hezuogongying/llm-skills-manager
"""
    )
