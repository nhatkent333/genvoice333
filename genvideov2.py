# genvideo.py (fix padding lỗi OSError)
import os
import argparse
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips,
    CompositeAudioClip, concatenate_audioclips, AudioClip
)
import numpy as np

def make_slide_in(img_path, duration, direction="left", transition=1):
    clip = ImageClip(img_path).set_duration(duration)
    w, h = clip.size

    if direction == "left":
        start_pos, end_pos = (-w, 0), (0, 0)
    elif direction == "right":
        start_pos, end_pos = (w, 0), (0, 0)
    elif direction == "top":
        start_pos, end_pos = (0, -h), (0, 0)
    elif direction == "bottom":
        start_pos, end_pos = (0, h), (0, 0)
    else:
        start_pos, end_pos = (0, 0), (0, 0)

    clip = clip.set_position(lambda t: (
        start_pos[0] + (end_pos[0] - start_pos[0]) * min(1, t/transition),
        start_pos[1] + (end_pos[1] - start_pos[1]) * min(1, t/transition)
    ))
    return clip

def silent_audio(duration):
    """Tạo một đoạn im lặng"""
    return AudioClip(lambda t: np.zeros((len(t), 2)), duration=duration, fps=44100)

def generate_video(images_dir, voices_dir, bg_music_path, output_path):
    images = sorted([f for f in os.listdir(images_dir) if f.endswith(".png")],
                    key=lambda x: int(x.split("_")[1].split(".")[0]))
    voices = sorted([f for f in os.listdir(voices_dir) if f.endswith(".mp3")],
                    key=lambda x: int(x.split("_")[1].split(".")[0]))

    video_clips = []
    voice_clips = []
    voice_durations = []

    for idx, (img, voice) in enumerate(zip(images, voices), start=1):
        voice_clip = AudioFileClip(os.path.join(voices_dir, voice))

        # Thêm 0.5s im lặng cuối voice
        padded_voice = CompositeAudioClip([voice_clip, silent_audio(0.5).set_start(voice_clip.duration)])
        total_dur = voice_clip.duration + 0.5

        voice_durations.append(total_dur)

        if idx % 2 == 1:
            img_clip = make_slide_in(os.path.join(images_dir, img), total_dur, "left")
        else:
            img_clip = make_slide_in(os.path.join(images_dir, img), total_dur, "top")

        video_clips.append(img_clip)
        voice_clips.append(padded_voice)

    final_video = concatenate_videoclips(video_clips, method="compose")
    voice_track = concatenate_audioclips(voice_clips)

    total_duration = sum(voice_durations)
    bg_music = AudioFileClip(bg_music_path)

    if bg_music.duration < total_duration:
        n_loops = int(total_duration // bg_music.duration) + 1
        bg_music = concatenate_audioclips([bg_music] * n_loops)
        bg_music = bg_music.subclip(0, total_duration)
    else:
        bg_music = bg_music.subclip(0, total_duration)

    final_audio = CompositeAudioClip([voice_track, bg_music.volumex(0.2)])
    final_video = final_video.set_audio(final_audio)

    final_video.write_videofile(output_path, fps=24, logger=None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_dir", required=True)
    parser.add_argument("--voices_dir", required=True)
    parser.add_argument("--bg_music", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()
    generate_video(args.images_dir, args.voices_dir, args.bg_music, args.output)
