import streamlit as st
import dashscope
from dashscope import Generation

# 页面配置
st.set_page_config(page_title="AI会议纪要助手", page_icon="📝")
st.title("📝 AI会议纪要助手")

# 侧边栏：API Key 输入
api_key = st.sidebar.text_input("DashScope API Key", type="password")

# 示例会议记录文本
EXAMPLE_TEXT = """项目周会 - 2025年4月2日
参会人：张三(产品)、李四(开发)、王五(测试)
讨论内容：
1. 上周开发的AI会议纪要功能已经完成初版，但识别准确率只有80%。
2. 用户反馈待办事项提取经常漏掉负责人。
3. 决定：下周三前由李四优化prompt，王五准备20条测试用例。
4. 下周五发布内测版本，邀请10个内部用户试用。"""

# 示例数据区域
with st.expander("🎯 点击试用示例会议记录"):
    st.text(EXAMPLE_TEXT)
    if st.button("使用此示例"):
        st.session_state.meeting_text = EXAMPLE_TEXT

# 主区域文本输入框
meeting_input = st.text_area(
    "粘贴会议记录",
    height=250,
    key="meeting_text"
)

# 生成按钮
if st.button("生成会议纪要"):
    current_text = st.session_state.get("meeting_text", "")

    # 输入校验
    if not api_key:
        st.error("请在侧边栏输入 DashScope API Key。")
    elif not current_text.strip():
        st.error("请输入会议记录内容。")
    else:
        # 构建 prompt
        prompt = f"""你是一个专业的会议纪要助手。请根据以下会议记录，输出：
1. 摘要（3-5句话概括核心内容）
2. 待办事项（每条包括：任务、负责人、截止时间。如果原文没有明确写负责人或截止时间，写"待定"）
3. 关键决策（列出会议中明确做出的决定）

会议记录：
{current_text}"""

        try:
            # 调用通义千问 API
            dashscope.api_key = api_key
            response = Generation.call(
                model="qwen-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )

            if response.status_code == 200:
                # 兼容两种响应结构：choices 列表 或 直接 text 字段
                output = response.output
                if output.choices:
                    result = output.choices[0].message.content
                else:
                    result = output.text

                # 显示结果
                st.subheader("📌 会议纪要")
                st.markdown(result)

                # 下载按钮
                st.download_button(
                    label="下载纪要",
                    data=result,
                    file_name="meeting_notes.md",
                    mime="text/markdown"
                )
            else:
                st.error(f"API调用失败，请检查Key或网络（状态码：{response.status_code}）")

        except Exception as e:
            st.error(f"API调用失败，请检查Key或网络（{e}）")
