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
    HTTPリクエストを処理するクラス。BaseHTTPRequestHandlerを継承。
    do_GET()はGETリクエスト受信時にフレームワークから自動で呼び出される。
    """
    def do_GET(self):
        if self.path == '/stream.mjpg':
            # 外側のHTTPヘッダーを送信（最初に1回だけ）
            # Age:0 はキャッシュなし、Cache-Control/Pragmaはブラウザ・プロキシへのキャッシュ禁止指示
            # multipart/x-mixed-replace はMJPEGストリーミング用のContent-Type
            # boundary=FRAME でフレームの区切り文字を指定
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()

            try:
                # クライアントが切断するまでフレームを送り続ける
                while True:
                    # 新しいフレームが来るまで待機（Conditionがロック解放→待機→再取得を管理）
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame

                    # 1フレーム分のミニヘッダーとJPEGデータを送信
                    # 構造: --FRAME\r\n + ミニヘッダー + 空行 + JPEGデータ + \r\n
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()        # ミニヘッダーの終わり（空行を出力）
                    self.wfile.write(frame)   # JPEGバイナリデータ
                    self.wfile.write(b'\r\n') # フレームの区切り（end_headers()とは別物）

            except Exception as e:
                # while Trueループはクライアント切断時の例外で終了する
                print(f'クライアント切断: {self.client_address}')
        else:
            # /stream.mjpg 以外のパスは404を返す（send_error()内部でend_headers()を呼ぶ）
            self.send_error(404)

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
