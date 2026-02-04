"""
Tests for system control operations.
"""

import pytest
from unittest.mock import patch, MagicMock
from jarvis.automation.system_control import SystemControl

class TestSystemControl:
    
    @pytest.fixture
    def sys_ctrl(self):
        return SystemControl()
    
    def test_screenshot(self, sys_ctrl):
        with patch('jarvis.automation.system_control.pyautogui') as mock_pg:
            mock_screenshot = MagicMock()
            mock_pg.screenshot.return_value = mock_screenshot
            
            success, msg = sys_ctrl.screenshot("test.png")
            assert success is True
            mock_screenshot.save.assert_called_once()
    
    def test_mute(self, sys_ctrl):
        with patch('jarvis.automation.system_control.pyautogui') as mock_pg:
            success, msg = sys_ctrl.mute()
            assert success is True
            mock_pg.press.assert_called_with('volumemute')
    
    def test_volume_up_down(self, sys_ctrl):
        # These may be stubbed on non-Windows
        success_up, _ = sys_ctrl.volume_up()
        success_down, _ = sys_ctrl.volume_down()
        
        # Should return tuple format
        assert isinstance(success_up, bool)
        assert isinstance(success_down, bool)
    
    def test_shutdown_safety(self, sys_ctrl):
        # Should require confirmation and settings flag
        with patch('jarvis.automation.system_control.ENABLE_SYSTEM_SHUTDOWN', False):
            success, msg = sys_ctrl.shutdown(confirm=True)
            assert success is False
            assert "disabled" in msg.lower()