import os
import argparse
from google.colab import auth
from googleapiclient.discovery import build


def export_slides_to_png(slide_id, output_dir):
    """Xuất từng slide thành PNG và lưu vào output_dir."""
    # Xác thực tài khoản Google
    try:
        auth.authenticate_user()
    except Exception:
        print("⚠️ Không chạy trên Colab, bỏ qua bước auth")

    service = build("slides", "v1")
    drive_service = build("drive", "v3")

    # Lấy thông tin trình chiếu
    presentation = service.presentations().get(presentationId=slide_id).execute()
    slide_count = len(presentation.get("slides", []))

    # Tạo thư mục nếu chưa có
    os.makedirs(output_dir, exist_ok=True)

    print(f"📑 Tổng số slide: {slide_count}")
    for i in range(slide_count):
        page_object_id = presentation["slides"][i]["objectId"]

        # Xuất slide sang PNG (sử dụng Drive API export)
        request = drive_service.files().export_media(
            fileId=slide_id,
            mimeType="image/png"
        )

        # Lưu file
        file_path = os.path.join(output_dir, f"slide_{i+1}.png")
        with open(file_path, "wb") as f:
            f.write(request.execute())

        print(f"✅ Saved {file_path}")


def main():
    parser = argparse.ArgumentParser(description="Export Google Slides to PNG")
    parser.add_argument("--slide_id", required=True, help="Google Slide ID")
    parser.add_argument("--output_dir", default="/content/pngslide", help="Output folder for PNG files")
    args = parser.parse_args()

    export_slides_to_png(args.slide_id, args.output_dir)


if __name__ == "__main__":
    main()
