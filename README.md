```
# 📌 Cell chạy GenVoice Colab với lựa chọn giọng đọc

# 1. Tạo file apikey.txt

# 2. Tạo file script.txt

# 3. Clone repo
!git clone https://github.com/nhatkent333/genvoice333.git
%cd genvoice333

# 4. Chọn giọng đọc và chạy script
VOICE_NAME = "Aoede"  # 👉 đổi sang Kore, Charon, Fenrir...
!python genvoice333.py --voice $VOICE_NAME

# 5. Kiểm tra file mp3 đã tạo
!ls -lh content/genvoice/
```
