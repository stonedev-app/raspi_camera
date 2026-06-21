# 開発メモ

## Python仮想環境作成

※Macのみ。テスト実行用

```bash
python -m venv .venv
source .venv/bin/activate
```

## テスト実行

```bash
cd src
python -m unittest tests.test_streaming_server -v
```

`picamera2` は `sys.modules` にダミーを挿入
