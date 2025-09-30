import argparse
from google.colab import auth
from googleapiclient.discovery import build


def get_slide_notes(service, presentation_id):
    """Trích xuất toàn bộ ghi chú từ Google Slides."""
    presentation = service.presentations().get(
        presentationId=presentation_id
    ).execute()

    notes_list = []
    slides = presentation.get("slides", [])

    for idx, slide in enumerate(slides, start=1):
        notes_text = ""
        notes_page = slide.get("slideProperties", {}).get("notesPage")

        if notes_page:
            shapes = notes_page.get("pageElements", [])
            for shape in shapes:
                if "shape" in shape:
                    text_elements = (
                        shape["shape"]
                        .get("text", {})
                        .get("textElements", [])
                    )
                    for elem in text_elements:
                        if "textRun" in elem:
                            notes_text += elem["textRun"]["content"]

        notes_list.append(notes_text.strip())

    return notes_list


def export_to_txt(notes, output_path):
    """Xuất danh sách ghi chú ra TXT, mỗi ghi chú 1 dòng."""
    with open(output_path, "w", encoding="utf-8") as f:
        for note in notes:
            if note.strip():
                f.write(note.strip() + "\n")

    print(f"✅ Notes exported to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract notes from Google Slides and export to TXT")
    parser.add_argument("--slide_id", required=True, help="Google Slide ID")
    parser.add_argument("--output_script_path", required=True, help="Path to save script.txt")
    args = parser.parse_args()

    # Authenticate only when running in Colab
    try:
        auth.authenticate_user()
    except Exception:
        print("⚠️ Skipping Colab auth (not running in Colab)")

    service = build("slides", "v1")
    notes = get_slide_notes(service, args.slide_id)
    export_to_txt(notes, args.output_script_path)


if __name__ == "__main__":
    main()
