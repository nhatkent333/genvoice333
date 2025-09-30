import os
import argparse
from googleapiclient.discovery import build
import requests

def export_slides_to_png(slide_id, output_dir):
    """Xuất từng slide trong Google Slides thành PNG."""
    service = build("slides", "v1")

    # Lấy thông tin presentation
    presentation = service.presentations().get(presentationId=slide_id).execute()
    slides = presentation.get("slides", [])
    os.makedirs(output_dir, exist_ok=True)

    print(f"📑 Tổng số slide: {len(slides)}")

    for i, slide in enumerate(slides, start=1):
        page_id = slide.get("objectId")

        # Lấy thumbnail của từng slide
        thumbnail = service.presentations().pages().getThumbnail(
            presentationId=slide_id,
            pageObjectId=page_id,
            thumbnailProperties_thumbnailSize="LARGE"
        ).execute()

        content_url = thumbnail.get("contentUrl")

        # Tải về PNG
        file_path = os.path.join(output_dir, f"slide_{i}.png")
        r = requests.get(content_url)
        with open(file_path, "wb") as f:
            f.write(r.content)

        print(f"✅ Saved {file_path}")


def main():
    parser = argparse.ArgumentParser(description="Export Google Slides to PNG")
    parser.add_argument("--slide_id", required=True, help="Google Slide ID")
    parser.add_argument("--output_dir", default="/content/pngslide", help="Output folder")
    args = parser.parse_args()

    export_slides_to_png(args.slide_id, args.output_dir)


if __name__ == "__main__":
    main()
