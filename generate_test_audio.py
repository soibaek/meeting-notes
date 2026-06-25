import base64
import wave
import numpy as np

def generate_test_audio(duration=2, sample_rate=16000):
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    freq = 440
    audio_data = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    
    with wave.open("test_audio.wav", "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    
    with open("test_audio.wav", "rb") as f:
        audio_bytes = f.read()
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
    
    print(f"生成的音频文件大小: {len(audio_bytes) / 1024:.2f} KB")
    print(f"Base64 编码长度: {len(base64_audio)}")
    print("\nBase64 音频数据:")
    print(f"data:audio/wav;base64,{base64_audio}")
    
    return base64_audio

if __name__ == "__main__":
    generate_test_audio()