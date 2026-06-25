import streamlit as st
import dashscope
from dashscope import Generation
from dashscope import MultiModalConversation
import logging
import base64
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 页面配置
st.set_page_config(page_title="AI会议纪要助手", page_icon="📝")
st.title("📝 AI会议纪要助手")

api_key = "sk-1935e30f9bf14e088448600a8b915770"

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

# 音频上传区域
st.subheader("🎤 上传音频文件（语音转文字）")

# 文件上传容器
upload_container = st.container()
with upload_container:
    col1, col2 = st.columns([4, 2])
    with col1:
        uploaded_audio = st.file_uploader(
            "",
            type=["mp3", "wav", "m4a", "aac"],
            label_visibility="collapsed",
            help="支持 mp3、wav、m4a、aac 格式"
        )
    with col2:
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 12px; border-radius: 8px; text-align: center;">
            <div style="font-size: 12px; color: #666;">支持格式</div>
            <div style="font-size: 14px; font-weight: bold; color: #333;">mp3 / wav / m4a / aac</div>
            <div style="font-size: 12px; color: #999;">最大 25MB</div>
        </div>
        """, unsafe_allow_html=True)

# 测试按钮
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.info("💡 如果没有音频文件，可以点击右侧按钮使用测试数据验证功能")
with col2:
    if st.button("🧪 测试语音识别"):
        # 使用真实的测试音频文件
        test_audio_path = "e:\\AI\\Claude\\会议纪要\\test_meeting_audio.wav"
        
        if not os.path.exists(test_audio_path):
            st.error("测试音频文件不存在，请先运行 create_real_test_audio.py 生成测试音频")
            logging.error("[测试失败] 测试音频文件不存在")
        else:
            with open(test_audio_path, "rb") as f:
                test_audio_data = f.read()
                test_audio_base64 = base64.b64encode(test_audio_data).decode('utf-8')
            
            with st.spinner("正在使用测试数据验证语音识别功能..."):
                try:
                    logging.info("[测试语音识别] 开始使用测试数据")
                    logging.info(f"[API Key检查] 长度={len(api_key)}, 前10位={api_key[:10]}")
                    logging.info(f"[音频信息] 文件大小={len(test_audio_data)/1024:.2f}KB, Base64长度={len(test_audio_base64)}")
                    
                    dashscope.api_key = api_key
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"audio": f"data:audio/wav;base64,{test_audio_base64}"},
                                {"text": "请将这段音频内容转写成文字。"}
                            ]
                        }
                    ]
                    
                    logging.info("[API调用] 模型=qwen-audio-turbo, 消息构建完成")
                    response = MultiModalConversation.call(
                        model='qwen-audio-turbo',
                        messages=messages,
                    )
                    
                    logging.info(f"[测试语音识别完成] status_code={response.status_code}")
                    
                    if response.status_code == 200:
                        transcript = response.output.choices[0].message.content[0]["text"]
                        st.session_state.meeting_text = f"【测试结果】{transcript}"
                        st.success("测试完成！识别结果已填充到输入框。")
                        st.info("注意：由于测试音频是模拟数据，实际识别结果可能不完整。请使用真实音频文件进行完整测试。")
                    else:
                        st.error(f"测试失败（状态码：{response.status_code}）")
                        logging.error(f"[测试失败] status_code={response.status_code}")
                        
                        # 根据状态码提供具体建议
                        if response.status_code == 401:
                            st.warning("🔑 API Key 无效或已过期，请检查代码中的 API Key")
                        elif response.status_code == 403:
                            st.warning("🚫 API Key 没有语音识别权限，请检查账号权限")
                        elif response.status_code == 404:
                            st.warning("🔍 模型 qwen-audio-turbo 不可用，请检查模型名称")
                        elif response.status_code == 400:
                            st.warning("📝 请求参数错误，可能是音频数据格式问题")
                        
                        if hasattr(response, 'message'):
                            st.error(f"错误详情：{response.message}")
                            logging.error(f"[错误详情] {response.message}")
                        
                except Exception as e:
                    st.error(f"测试失败：{e}")
                    logging.error(f"[测试异常] error={e}, type={type(e).__name__}")
                    
                    # 提供详细的错误诊断
                    if "Invalid API Key" in str(e):
                        st.warning("🔑 API Key 格式错误或无效，请检查代码第12行的 api_key")
                    elif "timeout" in str(e).lower():
                        st.warning("⏱️ 请求超时，请检查网络连接")
                    elif "connection" in str(e).lower():
                        st.warning("🌐 网络连接失败，请检查网络设置")
                    elif "module" in str(e).lower():
                        st.warning("📦 缺少依赖包，请运行：pip install --upgrade dashscope")

if uploaded_audio is not None:
    file_size = uploaded_audio.size / (1024 * 1024)
    
    if file_size > 25:
        st.markdown("""
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 16px;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 24px; margin-right: 12px;">❌</span>
                <div>
                    <div style="font-weight: bold; color: #dc2626;">文件大小超过限制</div>
                    <div style="font-size: 14px; color: #991b1b;">当前文件：{:.2f} MB，最大支持：25 MB</div>
                </div>
            </div>
        </div>
        """.format(file_size), unsafe_allow_html=True)
    else:
        file_extension = uploaded_audio.name.split('.')[-1].upper()
        
        st.markdown("""
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 32px; margin-right: 16px;">🎵</span>
                <div>
                    <div style="font-weight: bold; color: #166534;">{} ({})</div>
                    <div style="font-size: 14px; color: #15803d;">文件大小：{:.2f} MB</div>
                </div>
            </div>
            <div style="background-color: #16a34a; color: white; padding: 8px 16px; border-radius: 6px; font-size: 12px; font-weight: bold;">
                {}
            </div>
        </div>
        """.format(uploaded_audio.name, file_extension, file_size, "已上传"), unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.info("💡 点击下方按钮开始语音识别，识别结果将自动填充到会议记录输入框")
        with col2:
            if st.button("🎧 开始语音识别", use_container_width=True):
                with st.spinner("🔄 正在识别音频内容，请稍候..."):
                    try:
                        audio_bytes = uploaded_audio.read()
                        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                        
                        logging.info(f"[语音识别开始] 文件={uploaded_audio.name}, size={file_size:.2f}MB")
                        logging.info(f"[音频信息] Base64长度={len(audio_base64)}")
                        
                        dashscope.api_key = api_key
                        messages = [
                            {
                                "role": "user",
                                "content": [
                                    {"audio": f"data:audio/{uploaded_audio.type.split('/')[-1]};base64,{audio_base64}"},
                                    {"text": "请将这段音频内容转写成文字。"}
                                ]
                            }
                        ]
                        
                        response = MultiModalConversation.call(
                            model='qwen-audio-turbo',
                            messages=messages,
                        )
                        
                        logging.info(f"[语音识别完成] status_code={response.status_code}")
                        
                        if response.status_code == 200:
                            transcript = response.output.choices[0].message.content[0]["text"]
                            st.session_state.meeting_text = transcript
                            
                            st.markdown("""
                            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; margin-top: 12px;">
                                <div style="display: flex; align-items: center;">
                                    <span style="font-size: 24px; margin-right: 12px;">✅</span>
                                    <div>
                                        <div style="font-weight: bold; color: #166534;">语音识别完成！</div>
                                        <div style="font-size: 14px; color: #15803d;">已自动填充到会议记录输入框</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            logging.info(f"[识别结果] 文本长度={len(transcript)}")
                        else:
                            st.error(f"语音识别失败（状态码：{response.status_code}）")
                            logging.error(f"[语音识别失败] status_code={response.status_code}")
                            
                            if response.status_code == 401:
                                st.warning("🔑 API Key 无效或已过期，请检查代码中的 API Key")
                            elif response.status_code == 403:
                                st.warning("🚫 API Key 没有语音识别权限")
                            
                    except Exception as e:
                        st.error(f"语音识别失败：{e}")
                        logging.error(f"[语音识别异常] error={e}, type={type(e).__name__}")

# 主区域文本输入框
meeting_input = st.text_area(
    "粘贴会议记录（或通过音频识别自动填充）",
    height=250,
    key="meeting_text"
)

# 生成按钮
if st.button("生成会议纪要"):
    current_text = st.session_state.get("meeting_text", "")

    # 输入校验
    if not current_text.strip():
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
            logging.info(f"[API调用开始] model=qwen-turbo, prompt_length={len(prompt)}")
            logging.info(f"[API调用] api_key前10位={api_key[:10]}...")
            
            dashscope.api_key = api_key
            response = Generation.call(
                model="qwen-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            logging.info(f"[API调用完成] status_code={response.status_code}")
            logging.info(f"[API响应] output={response.output}")

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
            logging.error(f"[API调用异常] error={e}, type={type(e).__name__}")
            st.error(f"API调用失败，请检查Key或网络（{e}）")
