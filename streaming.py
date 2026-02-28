import io
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from time import sleep

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None # 最新のフレームを保存
        self.condition = Condition() # スレッド同期用

    def write(self, buf):
        with self.condition:
            self.frame = buf # 最新フレームを保存
            self.condition.notify_all()

# テスト
print("=== カメラとStreamingOutputの接続テスト ===")

print("1. StreamingOutput作成...")
output = StreamingOutput()

print("2. カメラ初期化...")
picam2 = Picamera2()

print("3. 設定...")
config = picam2.create_video_configuration(
    main = {"size": (640, 480)}
)
picam2.configure(config)

print("4. 録画開始...")
picam2.start_recording(MJPEGEncoder(), FileOutput(output))

print("5. 3秒間録画中...")
for i in range(3):
    sleep(1)
    if output.frame:
        print(f" {i+1}秒: フレームサイズ = {len(output.frame)} バイト")
    else:
        print(f" {i+1}秒: まだフレームなし")


print("6. 録画停止...")
picam2.stop_recording()

print("\n成功! カメラからのデータがStreamingOutputに書き込まれました")

