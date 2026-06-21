## 開発ワークフロー

picamera2ライブラリに依存しているため、**Raspberry Piでのみ実行可能**。

### Raspberry Piとのファイル同期

```bash
# 開発機 → Raspberry Pi へアップロード
./sync.sh upload

# Raspberry Pi → 開発機 へダウンロード
./sync.sh download
```
