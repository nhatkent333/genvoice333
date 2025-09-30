import argparse
import os

from google.colab import auth
from googleapiclient.discovery import build

def extract_notes_oauth(slide_id, output_path="script.txt"):
    # Xác thực bằng popup login
    auth.authenticate_user()

    # Tạo service Slides API
    service = build("slides", "v1")

    # Gọi API lấy presentation
    presentation = service.presentations().get(presentationId=slide_id).execute()
    slides = presentation.get("slides", [])

    notes_list = []

    for idx, slide in enumerate(slides, start=1):
        notes = ""
        notes_page = slide.get("slideProperties", {}).get("notesPage")

        if notes_page:
            shapes = notes_page.get("pageElements", [])
            for shape in shapes:
                text_content = shape.get("shape", {}).get("text", {}).get("textElements", [])
                for elem in text_content:
                    if "textRun" in elem:
                        notes += elem["textRun"].get("content", "")

        if notes.strip():
            notes_list.append(f"Slide {idx}:\n{notes.strip()}")

    if not notes_list:
        print("[INFO] Không tìm thấy ghi chú nào trong Google Slides.")
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n---\n".join(notes_list))
        print(f"[DONE] Đã lưu ghi chú vào {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract speaker notes from Google Slides (OAuth version)")
    parser.add_argument("--slide_id", required=True, help="Google Slide ID")
    parser.add_argument("--output", default="script.txt", help="Output file path")

    args = parser.parse_args()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    extract_notes_oauth(args.slide_id, args.output)
