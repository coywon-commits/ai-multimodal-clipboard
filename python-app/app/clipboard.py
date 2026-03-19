"""
클립보드 관리 모듈
이미지와 텍스트를 클립보드에 복사하는 기능
"""

import io
from PIL import Image
from pathlib import Path

# Windows 클립보드 API
import win32clipboard
import win32con


def copy_text_to_clipboard(text: str):
    """텍스트를 클립보드에 복사"""
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()


def copy_image_to_clipboard(image_path: Path):
    """이미지 파일을 클립보드에 복사"""
    # 이미지 열기
    image = Image.open(image_path)
    
    # RGBA -> RGB 변환 (클립보드는 알파 채널 지원 안 함)
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')
    
    # BMP 형식으로 변환 (Windows 클립보드용)
    output = io.BytesIO()
    image.save(output, 'BMP')
    bmp_data = output.getvalue()[14:]  # BMP 헤더 14바이트 제거
    output.close()
    
    # 클립보드에 복사
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, bmp_data)
    finally:
        win32clipboard.CloseClipboard()


def copy_image_bytes_to_clipboard(image_bytes: bytes):
    """이미지 바이트 데이터를 클립보드에 복사"""
    # 바이트에서 이미지 열기
    image = Image.open(io.BytesIO(image_bytes))
    
    # RGBA -> RGB 변환
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')
    
    # BMP 형식으로 변환
    output = io.BytesIO()
    image.save(output, 'BMP')
    bmp_data = output.getvalue()[14:]
    output.close()
    
    # 클립보드에 복사
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, bmp_data)
    finally:
        win32clipboard.CloseClipboard()


def get_clipboard_text() -> str:
    """클립보드에서 텍스트 가져오기"""
    win32clipboard.OpenClipboard()
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            return data
    except:
        pass
    finally:
        win32clipboard.CloseClipboard()
    return ""


def clear_clipboard():
    """클립보드 비우기"""
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
    finally:
        win32clipboard.CloseClipboard()
