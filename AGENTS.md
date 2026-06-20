## システム構成

開発機と Raspberry Pi は同一ネットワーク上にあり、rsync でファイルを同期して使用する。

```
[開発機]
  | コード編集・rsync転送
  v
[Raspberry Pi] --- [Arducam IMX219]
  | HTTP:8000 (MJPEG)
  v
[ブラウザ / クライアント]
```

## 開発ワークフロー

すべてのスクリプトはpicamera2ライブラリ（Raspberry Pi専用）に依存しているため、**Raspberry Pi上でのみ実行可能**。開発機では直接実行できない。

### Raspberry Piとのファイル同期

```bash
# 開発機 → Raspberry Pi へアップロード
./sync.sh upload

# Raspberry Pi → 開発機 へダウンロード
./sync.sh download
```
