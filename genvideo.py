import os
import argparse
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
)


def create_transition(clip, direction="left"):
    """Tạo hiệu ứng slide transition cho clip."""
    w, h = clip.size
    duration = 0.5  # thời gian transition

    if direction == "left":
        return clip.set_start(0).set_position(lambda t: (-w * (1 - t/duration), 0))
    elif direction == "top":
        return clip.set_start(0).set_position(lambda t: (0, -h * (1 - t/duration)))
    else:
        return clip


def generate_video(images_dir, voices_dir, bg_music_path, output_path):
    # Lấy danh sách ảnh và voice, sắp xếp theo thứ tự
    images = sorted([f for f in os.listdir(images_dir) if f.endswith(".png")])
    voices = sorted([f for f in os.listdir(voices_dir) if f.endswith(".mp3")])

    if len(images) != len(voices):
        raise ValueError("Số lượng ảnh và voice không khớp!")

    clips = []

    for i, (img, voice) in enumerate(zip(images, voices), start=1):
        img_path = os.path.join(images_dir, img)
        voice_path = os.path.join(voices_dir, voice)

        # Load voice
        audio = AudioFileClip(voice_path)
        duration = audio.duration

        # Load image và gắn audio
        img_clip = ImageClip(img_path).set_duration(duration).set_audio(audio)

        # Transition
        if i % 2 == 1:  # lẻ
            transition = img_clip.set_position(("center", "center"))
        else:  # chẵn
            transition = img_clip.set_position(("center", "center"))

        clips.append(transition)

    # Ghép tất cả scene
    video = concatenate_videoclips(clips, method="compose")

    # Thêm nhạc nền
    bg_music = AudioFileClip(bg_music_path).volumex(0.2)  # giảm volume nhạc
    final_audio = CompositeAudioClip([video.audio, bg_music.set_duration(video.duration)])
    final = video.set_audio(final_audio)

    # Xuất video
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")


def main():
    parser = argparse.ArgumentParser(description="Generate video from slides + voices + bg music")
    parser.add_argument("--images_dir", default="/content/pngslide", help="Folder chứa ảnh PNG")
    parser.add_argument("--voices_dir", default="/content/voiceoutput", help="Folder chứa voice mp3")
    parser.add_argument("--bg_music", default="/content/bg-music.mp3", help="File nhạc nền")
    parser.add_argument("--output", default="/content/final_video.mp4", help="Video đầu ra")
    args = parser.parse_args()

    generate_video(args.images_dir, args.voices_dir, args.bg_music, args.output)


if __name__ == "__main__":
    main()
