# genvideo.py
import os
import argparse
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips,
    CompositeAudioClip, concatenate_audioclips
)

def make_slide_in(img_path, duration, direction="left", transition=1):
    """
    Tạo hiệu ứng slide in cho ảnh tĩnh.
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

    clip = clip.set_position(lambda t: (
        start_pos[0] + (end_pos[0] - start_pos[0]) * min(1, t/transition),
        start_pos[1] + (end_pos[1] - start_pos[1]) * min(1, t/transition)
    ))

    return clip

def generate_video(images_dir, voices_dir, bg_music_path, output_path):
    # Lấy danh sách ảnh & voice, sort theo số thứ tự
    images = sorted([f for f in os.listdir(images_dir) if f.endswith(".png")],
                    key=lambda x: int(x.split("_")[1].split(".")[0]))
    voices = sorted([f for f in os.listdir(voices_dir) if f.endswith(".mp3")],
                    key=lambda x: int(x.split("_")[1].split(".")[0]))

    video_clips = []
    voice_clips = []
    voice_durations = []

    for idx, (img, voice) in enumerate(zip(images, voices), start=1):
        voice_clip = AudioFileClip(os.path.join(voices_dir, voice))

        # Cộng thêm 0.5 giây để tránh giật tiếng
        padded_duration = voice_clip.duration + 0.5
        voice_clip = voice_clip.set_duration(padded_duration)

        voice_durations.append(padded_duration)

        if idx % 2 == 1:
            img_clip = make_slide_in(os.path.join(images_dir, img), padded_duration, "left")
        else:
            img_clip = make_slide_in(os.path.join(images_dir, img), padded_duration, "top")

        video_clips.append(img_clip)
        voice_clips.append(voice_clip)

    # Nối video
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Nối voice track khớp từng slide
    voice_track = concatenate_audioclips(voice_clips)

    # Nhạc nền
    total_duration = sum(voice_durations)
    bg_music = AudioFileClip(bg_music_path)

    if bg_music.duration < total_duration:
        n_loops = int(total_duration // bg_music.duration) + 1
        bg_music = concatenate_audioclips([bg_music] * n_loops)
        bg_music = bg_music.subclip(0, total_duration)
    else:
        bg_music = bg_music.subclip(0, total_duration)

    # Mix audio (voice + bg), giảm âm lượng nhạc nền
    final_audio = CompositeAudioClip([voice_track, bg_music.volumex(0.2)])
    final_video = final_video.set_audio(final_audio)

    # Xuất video
    final_video.write_videofile(output_path, fps=24, logger=None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_dir", required=True, help="Folder chứa PNG slides")
    parser.add_argument("--voices_dir", required=True, help="Folder chứa voice MP3s")
    parser.add_argument("--bg_music", required=True, help="File nhạc nền")
    parser.add_argument("--output", required=True, help="Đường dẫn file video output")

    args = parser.parse_args()
    generate_video(args.images_dir, args.voices_dir, args.bg_music, args.output)
