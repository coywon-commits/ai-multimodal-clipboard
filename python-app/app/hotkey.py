"""
단축키 관리 모듈
글로벌 단축키 등록 및 처리 (pynput 사용)
"""

from pynput import keyboard
from typing import Callable, Dict, Optional


class HotkeyManager:
    """글로벌 단축키 관리 클래스"""
    
    def __init__(self):
        self.callbacks: Dict[str, Callable] = {}
        self._listener: Optional[keyboard.Listener] = None
        self._pressed_keys = set()
        self._debug_keys = False
    
    def register(self, hotkey: str, callback: Callable):
        """단축키 등록"""
        self.callbacks[hotkey] = callback
    
    def _on_press(self, key):
        """키 누름 처리"""
        # 제어 문자 -> 실제 키 매핑
        CTRL_CHAR_MAP = {
            '\x01': 'a', '\x02': 'b', '\x03': 'c', '\x04': 'd', '\x05': 'e',
            '\x06': 'f', '\x07': 'g', '\x08': 'h', '\x09': 'i', '\x0a': 'j',
            '\x0b': 'k', '\x0c': 'l', '\x0d': 'm', '\x0e': 'n', '\x0f': 'o',
            '\x10': 'p', '\x11': 'q', '\x12': 'r', '\x13': 's', '\x14': 't',
            '\x15': 'u', '\x16': 'v', '\x17': 'w', '\x18': 'x', '\x19': 'y',
            '\x1a': 'z',
        }
        
        try:
            key_name = None
            
            # 특수 키 처리
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                key_name = 'ctrl'
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt_gr:
                key_name = 'alt'
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                key_name = 'shift'
            else:
                # F1~F12 (pynput은 Key.f8 형태로 옴 — 여기 없으면 f8 단축키가 절대 안 먹음)
                for n in range(1, 13):
                    fk = getattr(keyboard.Key, f'f{n}', None)
                    if fk is not None and key == fk:
                        key_name = f'f{n}'
                        break
            if key_name is None and hasattr(key, 'char') and key.char:
                # 제어 문자 변환
                char = key.char
                if char in CTRL_CHAR_MAP:
                    key_name = CTRL_CHAR_MAP[char]
                else:
                    key_name = char.lower()
            elif key_name is None and hasattr(key, 'vk') and key.vk:
                # 가상 키 코드로 문자 추출 (F키는 위에서 이미 처리 — 여기서 덮어쓰면 안 됨)
                if 65 <= key.vk <= 90:  # A-Z
                    key_name = chr(key.vk).lower()
            
            if key_name:
                self._pressed_keys.add(key_name)
                if self._debug_keys:
                    print(f"키 누름: {key_name} | 현재: {self._pressed_keys}")
            
            # 단축키 확인
            self._check_hotkeys()
            
        except Exception as e:
            print(f"키 처리 오류: {e}")
    
    def _on_release(self, key):
        """키 뗌 처리"""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self._pressed_keys.discard('ctrl')
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self._pressed_keys.discard('alt')
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self._pressed_keys.discard('shift')
            else:
                for n in range(1, 13):
                    fk = getattr(keyboard.Key, f'f{n}', None)
                    if fk is not None and key == fk:
                        self._pressed_keys.discard(f'f{n}')
                        break
            if hasattr(key, 'char') and key.char:
                self._pressed_keys.discard(key.char.lower())
            elif hasattr(key, 'vk'):
                if 65 <= key.vk <= 90:
                    self._pressed_keys.discard(chr(key.vk).lower())
        except:
            pass
    
    def _check_hotkeys(self):
        """현재 눌린 키 조합이 등록된 단축키인지 확인"""
        for hotkey, callback in self.callbacks.items():
            keys = set(hotkey.lower().split('+'))
            # modifier/추가 키가 섞여도 필요한 키는 '포함'이면 실행하도록 완화
            if keys.issubset(self._pressed_keys):
                print(f"단축키 감지: {hotkey} | 현재: {self._pressed_keys}")
                # 콜백 실행 (예외가 나도 콘솔로 보이게 처리)
                try:
                    callback()
                except Exception as e:
                    print(f"단축키 콜백 오류({hotkey}): {e}")
                # 키 초기화 (중복 실행 방지)
                self._pressed_keys.clear()
                break
    
    def start(self):
        """단축키 리스닝 시작"""
        if self._listener:
            return
        
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()
        print("단축키 리스닝 시작됨 (붙여넣기 Ctrl+Shift+L, 초기화 Ctrl+Alt+M)")
    
    def stop(self):
        """단축키 리스닝 중지"""
        if self._listener:
            self._listener.stop()
            self._listener = None
            print("단축키 리스닝 중지됨")


# 기본 단축키 설정
DEFAULT_HOTKEYS = {
    'paste': 'ctrl+shift+l',
    'clear': 'ctrl+alt+m',
}


# 싱글톤 인스턴스
_hotkey_instance = None

def get_hotkey_manager() -> HotkeyManager:
    """HotkeyManager 싱글톤 인스턴스 반환"""
    global _hotkey_instance
    if _hotkey_instance is None:
        _hotkey_instance = HotkeyManager()
    return _hotkey_instance
