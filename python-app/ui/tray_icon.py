"""
시스템 트레이 아이콘 모듈
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, 
    QMessageBox, QWidget
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject


class TraySignals(QObject):
    """트레이 아이콘 시그널"""
    paste_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    quit_requested = pyqtSignal()


class SystemTrayApp(QSystemTrayIcon):
    """시스템 트레이 애플리케이션"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.signals = TraySignals()
        
        # 아이콘 설정
        self.setIcon(self._create_icon())
        
        # 메뉴 생성
        self._create_menu()
        
        # 툴팁 설정
        self.setToolTip("AI Clipboard Tool\n데이터 없음")
        
        # 더블클릭 이벤트
        self.activated.connect(self._on_activated)
    
    def _create_icon(self, has_data: bool = False) -> QIcon:
        """트레이 아이콘 생성"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 배경 원
        if has_data:
            painter.setBrush(QColor(76, 175, 80))  # 녹색 (데이터 있음)
        else:
            painter.setBrush(QColor(100, 100, 100))  # 회색 (데이터 없음)
        
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        
        # 클립보드 아이콘 (간단한 문자)
        painter.setPen(QColor(255, 255, 255))
        font = QFont('Arial', 28, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "📋")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _create_menu(self):
        """컨텍스트 메뉴 생성"""
        menu = QMenu()
        
        # 붙여넣기 액션
        paste_action = QAction("📋 붙여넣기 (Ctrl+Shift+L)", menu)
        paste_action.triggered.connect(self.signals.paste_requested.emit)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        # 초기화 액션
        clear_action = QAction("🗑️ 초기화 (Ctrl+Alt+M)", menu)
        clear_action.triggered.connect(self.signals.clear_requested.emit)
        menu.addAction(clear_action)
        
        menu.addSeparator()
        
        # 종료 액션
        quit_action = QAction("❌ 종료", menu)
        quit_action.triggered.connect(self.signals.quit_requested.emit)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
    
    def _on_activated(self, reason):
        """트레이 아이콘 활성화 이벤트"""
        if reason == QSystemTrayIcon.DoubleClick:
            # 더블클릭 시 붙여넣기
            self.signals.paste_requested.emit()
    
    def update_status(self, has_data: bool, summary: str = ""):
        """상태 업데이트"""
        self.setIcon(self._create_icon(has_data))
        
        if has_data:
            self.setToolTip(f"AI Clipboard Tool\n{summary}")
        else:
            self.setToolTip("AI Clipboard Tool\n데이터 없음")
    
    def show_notification(self, title: str, message: str, 
                         icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.Information):
        """알림 표시"""
        self.showMessage(title, message, icon, 3000)
