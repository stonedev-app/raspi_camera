"""
streaming_server.py のユニットテスト。
picamera2 は開発環境で動作しないため、sys.modules へのダミー挿入でモックする。
"""

import sys
import time
import threading
import unittest
from io import BytesIO
from unittest.mock import MagicMock

# picamera2 が存在しない環境でも import できるよう、先にモジュールを差し替える
sys.modules['picamera2'] = MagicMock()
sys.modules['picamera2.encoders'] = MagicMock()
sys.modules['picamera2.outputs'] = MagicMock()

# モック差し替え後に対象モジュールをインポート
from streaming_server import StreamingOutput, StreamingHandler  # noqa: E402


class TestStreamingOutput(unittest.TestCase):
    """StreamingOutput のスレッド同期ロジックをテストする"""

    def test_write_stores_frame(self):
        """write() が frame を最新のバイト列で更新すること"""
        output = StreamingOutput()
        data = b'\xff\xd8\xff'  # JPEGマジックバイト（ダミー）

        output.write(data)

        self.assertEqual(output.frame, data)

    def test_write_notifies_waiting_thread(self):
        """write() が待機中のスレッドに通知し、ブロックが解除されること"""
        output = StreamingOutput()
        received = []

        def waiter():
            # condition.wait() で新フレームを待機するスレッド（本番のHTTPハンドラーと同じパターン）
            with output.condition:
                output.condition.wait(timeout=2)
                received.append(output.frame)

        t = threading.Thread(target=waiter)
        t.start()

        output.write(b'frame_data')
        t.join(timeout=3)

        self.assertEqual(received, [b'frame_data'])

    def test_write_overwrites_previous_frame(self):
        """write() を複数回呼ぶと、frame が最後の値で上書きされること"""
        output = StreamingOutput()

        output.write(b'first')
        output.write(b'second')

        self.assertEqual(output.frame, b'second')


class TestStreamingHandler(unittest.TestCase):
    """StreamingHandler の HTTP レスポンスロジックをテストする"""

    def _make_handler(self, path: str):
        """
        StreamingHandler のインスタンスを生成するヘルパー。
        BaseHTTPRequestHandler の __init__ はソケット通信を前提とするため、
        インスタンス生成をスキップして属性を直接注入する。
        """
        handler = StreamingHandler.__new__(StreamingHandler)
        handler.path = path
        handler.wfile = BytesIO()
        # BrokenPipeError ハンドラで参照される属性
        handler.client_address = ('127.0.0.1', 0)

        # send_response / send_header / end_headers / send_error が書き込む先
        handler._headers_buffer = []

        # ヘッダー送信メソッドをモックで置き換え
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.send_error = MagicMock()

        return handler

    def test_invalid_path_returns_404(self):
        """/stream.mjpg 以外のパスは 404 を返すこと"""
        handler = self._make_handler('/invalid')

        handler.do_GET()

        handler.send_error.assert_called_once_with(404)

    def _run_stream_handler(self, handler, test_output):
        """
        do_GET を1フレームだけ処理して終了させるヘルパー。
        wfile を最初から BrokenPipeError を返すモックにしておき、
        フレームを1枚送ったところで自動的に例外ループを抜けさせる。
        """
        # 最初から BrokenPipeError を返す wfile にしておく
        # → do_GET が condition.wait() から復帰してフレームを書こうとした瞬間に終了
        handler.wfile = MagicMock()
        handler.wfile.write.side_effect = BrokenPipeError

        def feed():
            # do_GET が condition.wait() に入るのを待ってからフレームを送る
            time.sleep(0.05)
            test_output.write(b'\xff\xd8\xff')

        t = threading.Thread(target=feed)
        t.start()
        handler.do_GET()
        t.join(timeout=3)

    def test_stream_path_sends_200(self):
        """/stream.mjpg へのアクセスで 200 ステータスを送信すること"""
        import streaming_server as ss

        test_output = StreamingOutput()
        ss.output = test_output

        handler = self._make_handler('/stream.mjpg')
        self._run_stream_handler(handler, test_output)

        handler.send_response.assert_called_once_with(200)

    def test_stream_path_sends_mjpeg_content_type(self):
        """/stream.mjpg のレスポンスに multipart/x-mixed-replace ヘッダーが含まれること"""
        import streaming_server as ss

        test_output = StreamingOutput()
        ss.output = test_output

        handler = self._make_handler('/stream.mjpg')
        self._run_stream_handler(handler, test_output)

        # send_header の呼び出し一覧から Content-Type を探す
        calls = [str(c) for c in handler.send_header.call_args_list]
        self.assertTrue(
            any('multipart/x-mixed-replace' in c for c in calls),
            f"Content-Type ヘッダーが見つからない: {calls}"
        )


if __name__ == '__main__':
    unittest.main()
