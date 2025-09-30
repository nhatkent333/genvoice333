# genvideov2.py
import os
import argparse
import numpy as np
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
    concatenate_audioclips
)
from moviepy.audio.AudioClip import AudioArrayClip

def make_slide_in(img_path, duration, direction="left", transition=1):
    """
    Tạo hiệu ứng slide-in cho ảnh tĩnh.
    direction: "left", "right", "top", "bottom"
    transition: thời gian hiệu ứng (giây)
    """
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

    # position function: di chuyển từ start_pos -> end_pos trong 'transition' giây đầu
    clip = clip.set_position(lambda t: (
        start_pos[0] + (end_pos[0] - start_pos[0]) * min(1, t/transition),
        start_pos[1] + (end_pos[1] - start_pos[1]) * min(1, t/transition)
    ))
    return clip

def make_silence_array(duration, fps=44100):
    """Tạo AudioArrayClip chứa silence (stereo) dài `duration`."""
    n_samples = max(1, int(round(duration * fps)))
    arr = np.zeros((n_samples, 2), dtype=np.float32)
    return AudioArrayClip(arr, fps=fps)

def generate_video(images_dir, voices_dir, bg_music_path, output_path, bg_volume=0.2, transition=1.0, pad_s=0.5):
    # Lấy danh sách ảnh & voice, sort theo số (slide_1.png, voice_1.mp3)
    images = sorted([f for f in os.listdir(images_dir) if f.lower().endswith(".png")],
                    key=lambda x: int(x.split("_")[1].split(".")[0]))
    voices = sorted([f for f in os.listdir(voices_dir) if f.lower().endswith(".mp3")],
                    key=lambda x: int(x.split("_")[1].split(".")[0]))

    if len(images) != len(voices):
        raise ValueError("Số lượng ảnh và voice không khớp: %d images vs %d voices" % (len(images), len(voices)))

    video_clips = []
    padded_durations = []

    for idx, (img_fname, voice_fname) in enumerate(zip(images, voices), start=1):
        img_path = os.path.join(images_dir, img_fname)
        voice_path = os.path.join(voices_dir, voice_fname)

        voice_clip = AudioFileClip(voice_path)
        # tạo silence pad
        silence_clip = make_silence_array(pad_s).set_start(voice_clip.duration)
        # padded composite: voice + silence at end
        padded_audio = CompositeAudioClip([voice_clip, silence_clip])

        slide_dur = voice_clip.duration + pad_s
        padded_durations.append(slide_dur)

        # direction: lẻ => left, chẵn => top
        direction = "left" if (idx % 2 == 1) else "top"
        slide_clip = make_slide_in(img_path, slide_dur, direction=direction, transition=transition)
        slide_clip = slide_clip.set_audio(padded_audio)

        video_clips.append(slide_clip)

    # Nối các slide thành video; each clip already has its own audio (voice+silence)
    final_video = concatenate_videoclips(video_clips, method="compose")

    total_duration = sum(padded_durations)

    # Chuẩn bị bg music: cắt hoặc lặp để khớp total_duration
    bg_audio = AudioFileClip(bg_music_path)
    if bg_audio.duration < total_duration:
        n_loops = int(total_duration // bg_audio.duration) + 1
        bg_audio = concatenate_audioclips([bg_audio] * n_loops)
    bg_audio = bg_audio.subclip(0, total_duration).volumex(bg_volume)

    # final_video.audio là track voice (concatenated because each clip had audio)
    final_audio = CompositeAudioClip([final_video.audio, bg_audio])
    final_video = final_video.set_audio(final_audio)

    # Xuất video
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_dir", required=True, help="Folder chứa PNG slides")
    parser.add_argument("--voices_dir", required=True, help="Folder chứa voice MP3s")
    parser.add_argument("--bg_music", required=True, help="File nhạc nền")
    parser.add_argument("--output", required=True, help="Đường dẫn file video output")
    parser.add_argument("--bg_volume", type=float, default=0.2, help="Âm lượng nhạc nền (mặc định 0.2)")
    parser.add_argument("--transition", type=float, default=1.0, help="Thời lượng transition (giây)")
    parser.add_argument("--pad", type=float, default=0.5, help="Giây thêm vào cuối mỗi voice (padding silence)")

    args = parser.parse_args()
    generate_video(args.images_dir, args.voices_dir, args.bg_music, args.output,
                   bg_volume=args.bg_volume, transition=args.transition, pad_s=args.pad)
