```
# 📌 Cell chạy GenVoice Colab với lựa chọn giọng đọc

# 1. Clone repo
!git clone https://github.com/yourname/genvoice-colab.git
%cd genvoice-colab

# 2. Tạo file apikey.txt (thay bằng API key thật)
with open("apikey.txt", "w") as f:
    f.write("YOUR_API_KEY_HERE\n")

# 3. Tạo file script.txt
with open("script.txt", "w", encoding="utf-8") as f:
    f.write("Xin chào, đây là đoạn voice đầu tiên.\n")
    f.write("Đây là đoạn voice thứ hai.\n")
    f.write("Và đây là đoạn thứ ba.\n")

# 4. Chọn giọng đọc và chạy script
VOICE_NAME = "Aoede"  # 👉 đổi sang Kore, Charon, Fenrir...
!python genvoice333.py --voice $VOICE_NAME

# 5. Kiểm tra file mp3 đã tạo
!ls -lh content/genvoice/
```
