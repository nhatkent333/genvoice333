import os
import time
import ffmpeg
import wave
import argparse
from google import genai
from google.genai import types

# ==== ĐƯỜNG DẪN CẤU HÌNH ====
API_KEY_PATH = os.getenv("API_KEY_PATH", "content/apikey.txt")
SCRIPT_PATH = os.getenv("SCRIPT_PATH", "content/script.txt")
VOICE_OUTPUT_DIR = os.getenv("VOICE_OUTPUT_DIR", "content/genvoice")

# ==== HÀM XỬ LÝ ====
def load_gemini_api_keys(path=API_KEY_PATH):
    try:
        with open(path, "r", encoding="utf-8") as f:
            keys = [line.strip() for line in f if line.strip()]
        return keys
    except Exception:
        return []

def save_wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def convert_wav_to_mp3(wav_path, mp3_path):
    try:
        ffmpeg.input(wav_path).output(mp3_path).overwrite_output().run(quiet=True)
        os.remove(wav_path)
        return mp3_path
    except Exception as e:
        print(f"[WARN] Lỗi khi chuyển wav sang mp3: {e}. Giữ file wav.")
        return wav_path

# ==== CHẠY CHÍNH ====
def main(voice_name="Kore"):
    os.makedirs(VOICE_OUTPUT_DIR, exist_ok=True)

    api_keys = load_gemini_api_keys()
    if not api_keys:
        print("❌ Không tìm thấy API key trong apikey.txt")
        return
    api_count = len(api_keys)

    try:
        with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Lỗi đọc script.txt: {e}")
        return

    for fname in os.listdir(VOICE_OUTPUT_DIR):
        if fname.lower().endswith(".mp3"):
            try:
                os.remove(os.path.join(VOICE_OUTPUT_DIR, fname))
            except Exception as e:
                print(f"[WARN] Không xóa được file {fname}: {e}")

    for idx, text in enumerate(lines, 1):
        api_key_idx = (idx - 1) % api_count
        tried_keys = 0
        success = False
        response = None

        while tried_keys < api_count:
            api_key = api_keys[api_key_idx]
            print(f"[INFO] Generating voice {idx} (voice={voice_name}) (API key {api_key_idx+1}/{api_count}): {text}")
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice_name
                                )
                            )
                        )
                    )
                )
                success = True
                break
            except Exception as e:
                if (hasattr(e, 'status_code') and getattr(e, 'status_code', None) == 429) or \
                   ('RESOURCE_EXHAUSTED' in str(e) or '429' in str(e)):
                    print(f"[WARN] Quota exceeded với API key {api_key_idx+1}, thử key tiếp theo...")
                else:
                    print(f"[ERROR] Lỗi khi tạo voice {idx} với API key {api_key_idx+1}: {e}")
                    break
            api_key_idx = (api_key_idx + 1) % api_count
            tried_keys += 1

        if not success or not response:
            print(f"[ERROR] Bỏ qua dòng {idx} vì lỗi quota hoặc request thất bại.")
            continue

        audio_data = response.candidates[0].content.parts[0].inline_data.data
        wav_path = os.path.join(VOICE_OUTPUT_DIR, f"voice_{idx}.wav")
        save_wave_file(wav_path, audio_data)

        mp3_path = os.path.join(VOICE_OUTPUT_DIR, f"voice_{idx}.mp3")
        convert_wav_to_mp3(wav_path, mp3_path)

        print(f"✅ Voice {idx} đã lưu: {mp3_path}")

        if idx < len(lines):
            print("[INFO] Đợi 30 giây trước khi tạo voice tiếp theo...")
            time.sleep(30)

    print("🎉 Hoàn tất! Tất cả file voice đã được lưu trong content/genvoice/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice", type=str, default="Kore", help="Tên giọng đọc (VD: Kore, Aoede, Charon...)")
    args = parser.parse_args()
    main(voice_name=args.voice)
