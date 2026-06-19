## 概要

README.md 参照。

## 開発ワークフロー

すべてのスクリプトはpicamera2ライブラリ（Raspberry Pi専用）に依存しているため、**Raspberry Pi上でのみ実行可能**。PC上では直接実行できない。

### ファイル同期

```bash
# PC → Raspberry Pi へアップロード
make -C .make upload

# Raspberry Pi → PC へダウンロード
make -C .make download
```

`.make/Makefile`の接続設定: ホスト名・ユーザー名・リモートディレクトリは各自の環境に合わせて設定する（`.make/Makefile`を参照）

### Raspberry Pi上での実行

```bash
# メインのストリーミングサーバー起動
python src/streaming_server.py

# カメラ動作確認（test.jpg を撮影）
python src/tools/test_camera.py

# カメラ設定・解像度確認
python src/tools/check_resolution.py
```

ストリーミングURL: `http://raspberrypi:8000/stream.mjpg`（ホスト名は環境に合わせて変更）

## アーキテクチャ

### MJPEGストリーミングの仕組み（streaming_server.py）

```
Picamera2 → MJPEGEncoder → StreamingOutput → ThreadingTCPServer → HTTP clients
```

- `StreamingOutput`（`io.BufferedIOBase`サブクラス）: カメラからJPEGフレームを受け取るバッファ。`threading.Condition`でスレッド間同期を行い、HTTPハンドラーが新フレームを待機できるようにする。
- `StreamingHandler`（`BaseHTTPRequestHandler`）: `/stream.mjpg`へのGETリクエストに対し`multipart/x-mixed-replace`レスポンスを返し、フレームを無限送信し続ける。
- `socketserver.ThreadingTCPServer`で複数クライアントの同時接続に対応。

## ハードウェア・環境

README.md の「セットアップ」セクション参照。
