from picamera2 import Picamera2

picam2 = Picamera2()
picam2.start()

# 設定を確認
config = picam2.camera_configuration()
print("現在の設定:")
print(config)

picam2.stop()

