from picamera2 import Picamera2
import time

print("自動撮影開始...")
print("Ctrl+Cで停止")

picam2 = Picamera2()
picam2.start()
time.sleep(2) # 初期調整

try:
    count = 0
    while True:
        picam2.capture_file("latest.jpg")
        count += 1
        print(f"撮影 {count}枚目")
        time.sleep(1) # 1秒待機

except KeyboardInterrupt:
    print("\n停止中...")

finally:
    picam2.stop()
    print("完了!")

