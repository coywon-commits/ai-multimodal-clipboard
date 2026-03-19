"""
붙여넣기 자동화 모듈
텍스트와 이미지를 순차적으로 자동 붙여넣기
"""

import time
import pyautogui
from pathlib import Path
from typing import List, Callable, Optional

from .clipboard import (
    copy_image_to_clipboard,
    copy_text_to_clipboard,
    clear_clipboard,
    get_clipboard_text,
)

# pyautogui 설정
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


class PasteAutomation:
    """붙여넣기 자동화 클래스"""
    
    def __init__(self):
        # 붙여넣기 간 대기 시간 (초)
        self.text_delay = 1.0
        self.image_delay = 1.5
        
        # 콜백 함수들
        self.on_progress: Optional[Callable[[int, int, str], None]] = None
        self.on_complete: Optional[Callable[[int, int], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def paste_all(self, text: Optional[str], images: List[Path]) -> bool:
        """텍스트와 이미지를 순차적으로 붙여넣기"""
        total_items = (1 if text else 0) + len(images)
        
        try:
            print(f"paste_all(): 시작 | total_items={total_items} text_present={bool(text)} images_count={len(images)}")
            # 1. 클립보드 완전히 비우기
            clear_clipboard()
            print("paste_all(): 클립보드 비움 완료")
            time.sleep(0.2)
            
            # 2. 현재 마우스 위치 저장 (입력창 위치)
            mouse_x, mouse_y = pyautogui.position()
            print(f"paste_all(): 현재 마우스 위치 x={mouse_x} y={mouse_y}")
            
            # 3. 텍스트 붙여넣기 (win32clipboard로 통일)
            if text:
                # 텍스트도 win32clipboard로 통일 (포맷 충돌 방지)
                copy_text_to_clipboard(text)
                copied_back = get_clipboard_text()
                expected_preview = str(text or '').replace('\n', ' ')
                actual_preview = str(copied_back or '').replace('\n', ' ')
                if len(expected_preview) > 40:
                    expected_preview = expected_preview[:40] + '...'
                if len(actual_preview) > 40:
                    actual_preview = actual_preview[:40] + '...'
                print(
                    "paste_all(): 텍스트 클립보드 세팅 완료 | "
                    f"expect_len={len(text or '')} actual_len={len(copied_back or '')} | "
                    f"expected_preview='{expected_preview}' actual_preview='{actual_preview}'"
                )
                time.sleep(0.3)
                
                # 클릭해서 포커스 확실히 잡기
                pyautogui.click(mouse_x, mouse_y)
                time.sleep(0.5)  # 포커스 안정화 대기
                
                # 다시 한번 클릭 (더블 클릭 효과)
                pyautogui.click(mouse_x, mouse_y)
                time.sleep(0.3)
                
                # Ctrl+V 붙여넣기
                pyautogui.hotkey('ctrl', 'v')
                print("paste_all(): 텍스트 Ctrl+V 완료")
                time.sleep(self.text_delay)
            
            # 4. 이미지 순차 붙여넣기
            for i, image_path in enumerate(images):
                # 클립보드에 이미지 복사
                print(f"paste_all(): 이미지 {i+1}/{len(images)} 복사 시작 | {image_path}")
                copy_image_to_clipboard(image_path)
                time.sleep(0.3)
                
                # 클릭해서 포커스 유지
                pyautogui.click(mouse_x, mouse_y)
                time.sleep(0.5)
                
                # Ctrl+V 붙여넣기
                pyautogui.hotkey('ctrl', 'v')
                print(f"paste_all(): 이미지 {i+1} Ctrl+V 완료")
                time.sleep(self.image_delay)
            
            # 완료 콜백
            if self.on_complete:
                text_count = 1 if text else 0
                self.on_complete(text_count, len(images))
            
            return True
            
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            print(f"paste_all(): 예외 발생: {e}")
            return False
    
    def get_remaining_count(self) -> int:
        """호환성을 위한 메서드"""
        return 0
    
    def get_current_info(self) -> str:
        """호환성을 위한 메서드"""
        return ""


# 싱글톤 인스턴스
_paste_instance = None

def get_paste_automation() -> PasteAutomation:
    """PasteAutomation 싱글톤 인스턴스 반환"""
    global _paste_instance
    if _paste_instance is None:
        _paste_instance = PasteAutomation()
    return _paste_instance
