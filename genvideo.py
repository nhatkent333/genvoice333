# genvideo.py
import os
import argparse
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips,
    CompositeAudioClip, concatenate_audioclips
)
from moviepy.video.fx.all import slide_in

def generate_video(images_dir, voices_dir, bg_music_path, output_path):
    # Lấy danh sách file ảnh và voice, sort theo số
    images = sorted([f for f in os.listdir(images_dir) if f.endswith(".png")],
                    key=lambda x: int(x.split("_")[1].split(".")[0]))
    voices = sorted([f for f in os.listdir(voices_dir) if f.endswith(".mp3")],
                    key=lambda x: int(x.split("_")[1].split(".")[0]))

    video_clips = []
    voice_clips = []
    voice_durations = []

    for idx, (img, voice) in enumerate(zip(images, voices), start=1):
        voice_clip = AudioFileClip(os.path.join(voices_dir, voice))
        voice_durations.append(voice_clip.duration)

        img_clip = ImageClip(os.path.join(images_dir, img)).set_duration(voice_clip.duration)
        img_clip = img_clip.set_audio(voice_clip)

        # Transition
        transition_duration = 1
        if idx % 2 == 1:
            img_clip = slide_in(img_clip, transition_duration, "left")
        else:
            img_clip = slide_in(img_clip, transition_duration, "top")

        video_clips.append(img_clip)
        voice_clips.append(voice_clip)

    # Nối video
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Track voice tổng
    voice_track = CompositeAudioClip(voice_clips)

    # Nhạc nền
    total_duration = sum(voice_durations)
    bg_music = AudioFileClip(bg_music_path)

    if bg_music.duration < total_duration:
        n_loops = int(total_duration // bg_music.duration) + 1
        bg_music = concatenate_audioclips([bg_music] * n_loops)
        bg_music = bg_music.subclip(0, total_duration)
    else:
        bg_music = bg_music.subclip(0, total_duration)

    # Mix audio
    final_audio = CompositeAudioClip([voice_track, bg_music.volumex(0.3)])

    # Xuất video
    final_video = final_video.set_audio(final_audio)
    final_video.write_videofile(output_path, fps=24)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_dir", required=True, help="Folder chứa PNG slides")
    parser.add_argument("--voices_dir", required=True, help="Folder chứa voice MP3s")
    parser.add_argument("--bg_music", required=True, help="File nhạc nền")
    parser.add_argument("--output", required=True, help="Đường dẫn file video output")

    args = parser.parse_args()

    generate_video(args.images_dir, args.voices_dir, args.bg_music, args.output)
