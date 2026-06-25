import wave
import numpy as np
import base64

def create_test_audio():
    """创建一个更真实的测试音频文件"""
    duration = 2  # 2秒
    sample_rate = 16000  # 16kHz采样率
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    # 创建一个包含多个频率的音频，模拟语音
    freq1, freq2, freq3 = 440, 880, 1320  # 多个频率
    audio_data = (
        np.sin(2 * np.pi * freq1 * t) * 0.3 +
        np.sin(2 * np.pi * freq2 * t) * 0.2 +
        np.sin(2 * np.pi * freq3 * t) * 0.1
    ) * 32767
    
    # 添加一些噪声，使音频更真实
    noise = np.random.normal(0, 100, len(audio_data))
    audio_data = audio_data + noise
    
    audio_data = audio_data.astype(np.int16)
    
    # 保存为WAV文件
    with wave.open("test_meeting_audio.wav", "w") as wf:
        wf.setnchannels(1)  # 单声道
        wf.setsampwidth(2)  # 16位
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    
    # 生成Base64编码
    with open("test_meeting_audio.wav", "rb") as f:
        audio_bytes = f.read()
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
    
    print(f"✅ 测试音频文件已生成")
    print(f"📁 文件名: test_meeting_audio.wav")
    print(f"📊 文件大小: {len(audio_bytes) / 1024:.2f} KB")
    print(f"🔤 Base64长度: {len(base64_audio)}")
    print(f"⏱️  时长: {duration}秒")
    print(f"🎵 采样率: {sample_rate}Hz")
    
    # 保存Base64到文件
    with open("test_audio_base64.txt", "w") as f:
        f.write(base64_audio)
    
    print(f"💾 Base64数据已保存到: test_audio_base64.txt")
    
    return base64_audio

if __name__ == "__main__":
    create_test_audio()