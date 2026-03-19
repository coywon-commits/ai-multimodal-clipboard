"""
HTTP 서버 모듈
Chrome 확장에서 데이터를 직접 받기 위한 로컬 서버
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Callable, Optional

# 서버 포트
SERVER_PORT = 5757


class ClipboardHandler(BaseHTTPRequestHandler):
    """HTTP 요청 핸들러"""
    
    # 클래스 변수로 콜백 저장
    on_data_received: Optional[Callable] = None
    
    def log_message(self, format, *args):
        """로그 출력 비활성화 (콘솔 깨끗하게)"""
        pass
    
    def _send_cors_headers(self):
        """CORS 헤더 전송"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """CORS preflight 요청 처리"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """GET 요청 - 서버 상태 확인"""
        if self.path == '/status':
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'running', 'app': 'AI Clipboard'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """POST 요청 - 데이터 수신"""
        if self.path == '/data':
            try:
                # 데이터 읽기
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                text = data.get('text', '') or ''
                images = data.get('images', []) or []
                extractedAt = data.get('extractedAt', '') or ''
                text_preview = str(text).replace('\n', ' ')
                if len(text_preview) > 40:
                    text_preview = text_preview[:40] + '...'
                
                print(
                    f"HTTP /data 수신 | extractedAt={extractedAt} | text_len={len(text)} images={len(images)} | preview='{text_preview}'"
                )
                
                # 콜백 호출
                if ClipboardHandler.on_data_received:
                    ClipboardHandler.on_data_received(data)
                
                # 응답 전송
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'success': True, 'message': '데이터 저장 완료'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


class ClipboardServer:
    """클립보드 HTTP 서버"""
    
    def __init__(self, port: int = SERVER_PORT):
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self._running = False
    
    def set_data_callback(self, callback: Callable):
        """데이터 수신 콜백 설정"""
        ClipboardHandler.on_data_received = callback
    
    def start(self):
        """서버 시작 (별도 스레드)"""
        if self._running:
            return
        
        try:
            self.server = HTTPServer(('127.0.0.1', self.port), ClipboardHandler)
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            self._running = True
            print(f"HTTP 서버 시작: http://127.0.0.1:{self.port}")
        except Exception as e:
            print(f"서버 시작 실패: {e}")
    
    def _run(self):
        """서버 실행 (스레드에서 호출)"""
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"서버 오류: {e}")
    
    def stop(self):
        """서버 중지"""
        if self.server:
            self.server.shutdown()
            self._running = False
            print("HTTP 서버 중지됨")


# 싱글톤 인스턴스
_server_instance: Optional[ClipboardServer] = None


def get_server() -> ClipboardServer:
    """ClipboardServer 싱글톤 인스턴스 반환"""
    global _server_instance
    if _server_instance is None:
        _server_instance = ClipboardServer()
    return _server_instance
