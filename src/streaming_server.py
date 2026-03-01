# 標準ライブラリ
import io
import socketserver
from http import server
from threading import Condition

# 外部ライブラリ
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput

class StreamingOutput(io.BufferedIOBase):
    """
    カメラからのJPEGフレームを受け取るバッファ。
    io.BufferedIOBaseを継承することで、picamera2がファイルと同じように書き込める。
    Conditionによりスレッド間の同期を行い、HTTPハンドラーが新フレームを待機できるようにする。
    """

    def __init__(self):
        # 最新のJPEGフレームを保存する変数
        self.frame = None
        # スレッド間の待機・通知に使うCondition（ロック機能も兼ねる）
        self.condition = Condition()

    def write(self, buf):
        """
        picamera2から呼び出されるメソッド。io.BufferedIOBaseのwriteをオーバーライド。
        新しいフレームを保存し、待機中の全HTTPスレッドに通知する。
        with self.conditionでロックを取得・解放し、排他制御を行う。
        """
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    """
    HTTPリクエストを処理するクラス
    """
    def do_GET(self):
        if self.path == '/stream.mjpg':
            # MJPEGストリーミング
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()

            try:
                while True:
                    # 新しいフレームを待つ
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame

                    # ブラウザに送信
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')

            except Exception as e:
                print(f'クライアント切断: {self.client_address}')
        else:
            self.send_error(404)
            self.end_headers()

if __name__ == '__main__':
    print("=== MJPEGストリーミングサーバー ===")

    print("1. カメラ初期化...")
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(config)

    print("2. ストリーミング開始...")
    output = StreamingOutput()
    picam2.start_recording(MJPEGEncoder(), FileOutput(output))

    print("3. Webサーバー起動...")
    print()
    print("アクセス: http://<IPアドレス>:8000/stream.mjpg")
    print("停止: Ctr+C")
    print()

    try:
        address = ('', 8000)
        server = socketserver.ThreadingTCPServer(address, StreamingHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n停止中...")
    finally:
        picam2.stop_recording()
        print("完了!")
