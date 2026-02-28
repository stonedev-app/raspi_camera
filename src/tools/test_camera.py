from picamera2 import Picamera2
import time

print("カメラ初期化中...")
picam2 = Picamera2()

print("カメラ起動中...")
picam2.start()

print("2秒待機中...")
time.sleep(2)

print("撮影!")
picam2.capture_file("test.jpg")

print("カメラ停止")
picam2.stop()

