## 開発ワークフロー

すべてのスクリプトはpicamera2ライブラリ（Raspberry Pi専用）に依存しているため、**Raspberry Pi上でのみ実行可能**。開発機では直接実行できない。

### Raspberry Piとのファイル同期

```bash
# 開発機 → Raspberry Pi へアップロード
./sync.sh upload

# Raspberry Pi → 開発機 へダウンロード
./sync.sh download
```
