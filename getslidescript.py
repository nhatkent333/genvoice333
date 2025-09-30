import argparse
import requests
import sys

def extract_notes(slide_id, api_key, output_path="script.txt"):
    url = f"https://slides.googleapis.com/v1/presentations/{slide_id}?key={api_key}"

    try:
        resp = requests.get(url)
        resp.raise_for_status()
        presentation = resp.json()
    except Exception as e:
        print(f"[ERROR] Không thể gọi API: {e}")
        sys.exit(1)

    slides = presentation.get("slides", [])
    notes_list = []

    for idx, slide in enumerate(slides, start=1):
        notes = ""
        page_elements = slide.get("slideProperties", {})
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
    parser = argparse.ArgumentParser(description="Extract speaker notes from Google Slides")
    parser.add_argument("--slide_id", required=True, help="Google Slide ID")
    parser.add_argument("--api_key", required=True, help="Google Slides API key")
    parser.add_argument("--output", default="script.txt", help="Output file path")

    args = parser.parse_args()
    extract_notes(args.slide_id, args.api_key, args.output)
