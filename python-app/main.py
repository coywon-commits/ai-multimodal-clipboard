"""
AI Clipboard Tool - 메인 엔트리포인트
AI 채팅창의 텍스트와 이미지를 한 번에 복사하여 다른 AI 채팅창에 붙여넣기
"""

import sys
import os
import threading

# 현재 디렉토리를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

from ui.tray_icon import SystemTrayApp
from app.hotkey import get_hotkey_manager, DEFAULT_HOTKEYS
from app.paste import get_paste_automation
from app.server import get_server
from storage.manager import get_storage


class AIClipboardApp:
    """AI 클립보드 도구 메인 애플리케이션"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 컴포넌트 초기화
        self.storage = get_storage()
        self.paste_automation = get_paste_automation()
        self.hotkey_manager = get_hotkey_manager()
        self.server = get_server()

        # 핫키 요청(스레드 안전 이벤트 플래그)
        self._paste_requested = threading.Event()
        self._clear_requested = threading.Event()
        
        # HTTP 서버 시작 (Chrome 확장에서 데이터 직접 수신)
        self.server.set_data_callback(self._on_data_received)
        self.server.start()
        
        # 트레이 아이콘 생성
        self.tray = SystemTrayApp()
        
        # 시그널 연결
        self._connect_signals()
        
        # 단축키 등록
        self._register_hotkeys()
        
        # 상태 업데이트 타이머
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(2000)  # 2초마다 상태 확인

        # 핫키 요청 처리 타이머 (매우 짧은 주기)
        self.hotkey_timer = QTimer()
        self.hotkey_timer.timeout.connect(self._process_hotkey_requests)
        self.hotkey_timer.start(50)
        
        # 초기 상태 업데이트
        self._update_status()
    
    def _connect_signals(self):
        """시그널 연결"""
        self.tray.signals.paste_requested.connect(self._on_paste)
        self.tray.signals.clear_requested.connect(self._on_clear)
        self.tray.signals.quit_requested.connect(self._on_quit)
        
        # 붙여넣기 콜백 설정
        self.paste_automation.on_complete = self._on_paste_complete
        self.paste_automation.on_error = self._on_paste_error
    
    def _register_hotkeys(self):
        """단축키 등록"""
        try:
            self.hotkey_manager.register(
                DEFAULT_HOTKEYS['paste'], 
                lambda: self._paste_requested.set()
            )
            self.hotkey_manager.register(
                DEFAULT_HOTKEYS['clear'], 
                lambda: self._clear_requested.set()
            )
            self.hotkey_manager.start()
        except Exception as e:
            print(f"단축키 등록 실패: {e}")

    def _process_hotkey_requests(self):
        """pynput 콜백 스레드에서 set한 요청을 Qt 메인 스레드에서 처리"""
        if self._paste_requested.is_set():
            self._paste_requested.clear()
            self._on_paste()
        if self._clear_requested.is_set():
            self._clear_requested.clear()
            self._on_clear()
    
    def _update_status(self):
        """상태 업데이트"""
        has_data = self.storage.has_data()
        summary = self.storage.get_summary()
        self.tray.update_status(has_data, summary)
    
    def _on_paste(self):
        """붙여넣기 실행"""
        print("핫키: 붙여넣기 요청 들어옴(_on_paste)")
        if not self.storage.has_data():
            print("핫키: storage에 데이터 없음(has_data=False)")
            self.tray.show_notification(
                "AI Clipboard",
                "붙여넣을 데이터가 없습니다.\nChrome 확장에서 먼저 추출하세요."
            )
            return
        
        text = self.storage.get_text()
        images = self.storage.get_images()
        text_preview = str(text or '').replace('\n', ' ')
        if len(text_preview) > 40:
            text_preview = text_preview[:40] + '...'
        print(
            f"핫키: 데이터 로드됨 | text_len={len(text or '')} images={len(images)} | preview='{text_preview}'"
        )
        
        # 알림 표시 (3초 후 붙여넣기 시작)
        total = (1 if text else 0) + len(images)
        self.tray.show_notification(
            "AI Clipboard",
            f"3초 후 붙여넣기 시작!\n입력창에 마우스를 올려두세요!\n(총 {total}개 항목)"
        )
        
        # 3초 후 붙여넣기 실행
        QTimer.singleShot(3000, lambda: self._execute_paste(text, images))
    
    def _execute_paste(self, text, images):
        """실제 붙여넣기 실행"""
        print(f"붙여넣기 시작 | text_len={len(text or '')} images={len(images)}")
        success = self.paste_automation.paste_all(text, images)
        print(f"붙여넣기 결과(success)={success}")
        
        if not success:
            self.tray.show_notification(
                "AI Clipboard",
                "붙여넣기 중 오류가 발생했습니다."
            )
    
    def _on_paste_complete(self, text_count: int, image_count: int):
        """붙여넣기 완료 콜백"""
        parts = []
        if text_count:
            parts.append("텍스트")
        if image_count:
            parts.append(f"이미지 {image_count}개")
        
        self.tray.show_notification(
            "AI Clipboard",
            f"✅ 붙여넣기 완료: {', '.join(parts)}"
        )
    
    def _on_paste_error(self, error: str):
        """붙여넣기 오류 콜백"""
        self.tray.show_notification(
            "AI Clipboard - 오류",
            f"붙여넣기 실패: {error}"
        )
    
    def _on_clear(self):
        """데이터 초기화"""
        self.storage.clear()
        self._update_status()
        self.tray.show_notification(
            "AI Clipboard",
            "저장된 데이터가 초기화되었습니다."
        )
    
    def _on_data_received(self, data: dict):
        """Chrome 확장에서 데이터 수신"""
        text = data.get('text', '')
        images = data.get('images', [])
        extractedAt = data.get('extractedAt', '') or ''
        text_preview = str(text).replace('\n', ' ')
        if len(text_preview) > 40:
            text_preview = text_preview[:40] + '...'
        print(
            f"_on_data_received(): extractedAt={extractedAt} | text_len={len(text or '')} images={len(images)} | preview='{text_preview}'"
        )
        
        # 저장소에 저장
        self.storage.save_data(text, images)
        
        # 상태 업데이트 (메인 스레드에서 실행)
        QTimer.singleShot(0, self._update_status)
        
        # 알림 (메인 스레드에서 실행)
        def show_notification():
            total = (1 if text else 0) + len(images)
            self.tray.show_notification(
                "AI Clipboard",
                f"✅ 데이터 수신 완료!\n텍스트: {len(text)}자, 이미지: {len(images)}개"
            )
        QTimer.singleShot(0, show_notification)
    
    def _on_quit(self):
        """앱 종료"""
        self.hotkey_manager.stop()
        self.server.stop()
        self.app.quit()
    
    def run(self):
        """앱 실행"""
        # 트레이 아이콘 표시
        self.tray.show()
        
        # 시작 알림
        self.tray.show_notification(
            "AI Clipboard Tool",
            "앱이 시작되었습니다.\n"
            "Chrome 추출: Ctrl+Alt+O\n"
            "붙여넣기: Ctrl+Shift+L\n"
            "초기화: Ctrl+Alt+M"
        )
        
        # 이벤트 루프 시작
        return self.app.exec_()


def main():
    """메인 함수"""
    try:
        app = AIClipboardApp()
        sys.exit(app.run())
    except Exception as e:
        print(f"앱 실행 오류: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
