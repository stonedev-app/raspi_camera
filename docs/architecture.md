# アーキテクチャ

## MJPEGストリーミングの仕組み（streaming_server.py）

```
Picamera2 → MJPEGEncoder → StreamingOutput → ThreadingTCPServer → HTTP clients
```

- `StreamingOutput`（`io.BufferedIOBase`サブクラス）: カメラからJPEGフレームを受け取るバッファ。`threading.Condition`でスレッド間同期を行い、HTTPハンドラーが新フレームを待機できるようにする。
- `StreamingHandler`（`BaseHTTPRequestHandler`）: `/stream.mjpg`へのGETリクエストに対し`multipart/x-mixed-replace`レスポンスを返し、フレームを無限送信し続ける。
- `socketserver.ThreadingTCPServer`で複数クライアントの同時接続に対応。
