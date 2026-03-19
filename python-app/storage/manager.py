"""
로컬 저장소 관리 모듈
Chrome 확장에서 추출한 텍스트/이미지를 관리
"""

import os
import json
import base64
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class StorageManager:
    """로컬 저장소 관리 클래스"""
    
    def __init__(self):
        # 저장소 경로 설정 - 다운로드 폴더의 AIClipboard
        downloads_path = Path(os.path.expanduser('~')) / 'Downloads'
        self.base_path = downloads_path / 'AIClipboard'
        self.data_file = self.base_path / 'data.json'
        self.temp_images_path = Path(tempfile.gettempdir()) / 'AIClipboard_images'
        
        # 캐시된 데이터
        self._cached_data = None
        self._cached_time = None
        
        # 폴더 생성
        self._ensure_directories()
    
    def _ensure_directories(self):
        """필요한 디렉토리 생성"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.temp_images_path.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self) -> dict:
        """JSON 파일에서 데이터 로드"""
        if not self.data_file.exists():
            return {'text': '', 'images': []}
        
        try:
            # 파일 수정 시간 확인
            mtime = self.data_file.stat().st_mtime
            
            # 캐시가 유효하면 캐시 반환
            if self._cached_data and self._cached_time == mtime:
                return self._cached_data
            
            # 새로 로드
            data = json.loads(self.data_file.read_text(encoding='utf-8'))
            self._cached_data = data
            self._cached_time = mtime
            return data
        except (json.JSONDecodeError, IOError):
            return {'text': '', 'images': []}
    
    def get_text(self) -> Optional[str]:
        """저장된 텍스트 반환"""
        data = self._load_data()
        text = data.get('text', '')
        return text if text else None
    
    def get_images(self) -> List[Path]:
        """저장된 이미지를 임시 파일로 변환 후 경로 반환"""
        data = self._load_data()
        images_data = data.get('images', [])
        
        if not images_data:
            return []
        
        # 임시 폴더 비우기
        if self.temp_images_path.exists():
            shutil.rmtree(self.temp_images_path)
        self.temp_images_path.mkdir(parents=True, exist_ok=True)
        
        image_paths = []
        for i, img_data in enumerate(images_data):
            try:
                # data URL에서 base64 추출
                if img_data.startswith('data:'):
                    # data:image/png;base64,XXXX 형식
                    header, b64_data = img_data.split(',', 1)
                else:
                    b64_data = img_data
                
                # base64 디코딩
                img_bytes = base64.b64decode(b64_data)
                
                # 파일로 저장
                img_path = self.temp_images_path / f'img_{i+1:03d}.png'
                img_path.write_bytes(img_bytes)
                image_paths.append(img_path)
            except Exception as e:
                print(f"이미지 {i+1} 변환 실패: {e}")
        
        return image_paths
    
    def has_data(self) -> bool:
        """데이터가 있는지 확인"""
        data = self._load_data()
        return bool(data.get('text')) or bool(data.get('images'))
    
    def get_summary(self) -> str:
        """저장된 데이터 요약"""
        data = self._load_data()
        text = data.get('text', '')
        images = data.get('images', [])
        
        parts = []
        if text:
            preview = text[:30] + '...' if len(text) > 30 else text
            preview = preview.replace('\n', ' ')
            parts.append(f"텍스트")
        if images:
            parts.append(f"이미지 {len(images)}개")
        
        if not parts:
            return "저장된 데이터 없음"
        
        return " | ".join(parts)
    
    def save_data(self, text: str, images: list):
        """데이터 직접 저장 (HTTP 서버에서 호출)"""
        try:
            data = {
                'text': text or '',
                'images': images or [],
                'extractedAt': datetime.now().isoformat()
            }
            
            # JSON 파일로 저장
            self.data_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            
            # 캐시 초기화 (새 데이터 반영)
            self._cached_data = None
            self._cached_time = None
            
            print(f"데이터 저장 완료: 텍스트 {len(text or '')}자, 이미지 {len(images or [])}개")
            return True
        except Exception as e:
            print(f"데이터 저장 실패: {e}")
            return False
    
    def clear(self):
        """저장된 모든 데이터 삭제"""
        # data.json 삭제
        if self.data_file.exists():
            self.data_file.unlink()
        
        # 임시 이미지 폴더 비우기
        if self.temp_images_path.exists():
            shutil.rmtree(self.temp_images_path)
            self.temp_images_path.mkdir(parents=True, exist_ok=True)
        
        # 캐시 초기화
        self._cached_data = None
        self._cached_time = None


# 싱글톤 인스턴스
_storage_instance = None

def get_storage() -> StorageManager:
    """StorageManager 싱글톤 인스턴스 반환"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageManager()
    return _storage_instance
