"""
Tests for file manager operations using temp directories.
"""

import pytest
import tempfile
import os
from pathlib import Path
from jarvis.automation.file_manager import FileManager

class TestFileManager:
    
    @pytest.fixture
    def fm(self):
        return FileManager()
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_copy_files(self, fm, temp_dir):
        # Create source file
        src_file = temp_dir / "source.txt"
        src_file.write_text("test content")
        
        dst_file = temp_dir / "dest.txt"
        
        success, msg = fm.copy_files(str(src_file), str(dst_file))
        assert success is True
        assert dst_file.exists()
        assert dst_file.read_text() == "test content"
    
    def test_move_files(self, fm, temp_dir):
        src_file = temp_dir / "move_me.txt"
        src_file.write_text("move this")
        
        dst_file = temp_dir / "moved.txt"
        
        success, msg = fm.move_files(str(src_file), str(dst_file))
        assert success is True
        assert not src_file.exists()
        assert dst_file.exists()
    
    def test_delete_file(self, fm, temp_dir):
        target = temp_dir / "delete_me.txt"
        target.write_text("delete this")
        
        # Without confirmation should fail
        success, msg = fm.delete_path(str(target), confirm=False)
        assert success is False
        
        # With confirmation should succeed
        success, msg = fm.delete_path(str(target), confirm=True)
        assert success is True
        assert not target.exists()
    
    def test_copy_directory(self, fm, temp_dir):
        src_dir = temp_dir / "source_dir"
        src_dir.mkdir()
        (src_dir / "file.txt").write_text("content")
        
        dst_dir = temp_dir / "dest_dir"
        
        success, msg = fm.copy_files(str(src_dir), str(dst_dir))
        assert success is True
        assert (dst_dir / "file.txt").exists()
    
    def test_nonexistent_source(self, fm, temp_dir):
        success, msg = fm.copy_files(
            str(temp_dir / "nonexistent.txt"),
            str(temp_dir / "dest.txt")
        )
        assert success is False
        assert "doesn't exist" in msg