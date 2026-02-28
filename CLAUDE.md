# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Raspberry Pi Zero W + Arducam IMX219 カメラを使用した MJPEG ストリーミングサーバープロジェクト。
コードはPC上で開発し、rsyncでRaspberry Piに転送して実行する。

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
python streaming_server.py

# カメラ動作確認（test.jpg を撮影）
python test_camera.py

# カメラ設定・解像度確認
python check_resolution.py

# 自動連続撮影（latest.jpg に1秒ごと上書き保存）
python auto_capture.py
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

### 各スクリプトの役割

| ファイル | 用途 |
|---|---|
| `streaming_server.py` | 本番用MJPEGストリーミングサーバー（ポート8000） |
| `streaming.py` | StreamingOutput接続の動作確認テスト |
| `simple_server.py` | 静的ファイル配信用シンプルHTTPサーバー（ポート8000） |
| `test_camera.py` | カメラ基本動作確認（`test.jpg`を1枚撮影） |
| `auto_capture.py` | 1秒間隔で`latest.jpg`に上書き撮影するループ |
| `check_resolution.py` | 現在のカメラ設定を表示 |

## ハードウェア・環境

- Raspberry Pi OS Lite (Trixie)
- Arducam IMX219（8MP、CSI接続）
- `/boot/firmware/config.txt`に`camera_auto_detect=0`と`dtoverlay=imx219`が必要
- Picamera2インストール: `sudo apt install -y python3-picamera2 --no-install-recommends`
