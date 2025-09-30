```
# 1. Clone repo
!git clone https://github.com/nhatkent333/genvoice333.git
%cd genvoice333

# 2. Cài đặt dependencies
!pip install -r requirements.txt

# 3 cell chạy code

import os

# Chỉ định file và thư mục
os.environ["API_KEY_PATH"] = "/content/apikey.txt"
os.environ["SCRIPT_PATH"] = "/content/script.txt"
os.environ["VOICE_OUTPUT_DIR"] = "/content/genvoice"

# Chọn giọng đọc và chạy script
VOICE_NAME = "Aoede"  # 👉 đổi sang Kore, Charon, Fenrir...
!python genvoice333.py --voice $VOICE_NAME
```
