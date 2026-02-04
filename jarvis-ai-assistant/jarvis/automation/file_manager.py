"""
File manager for copy, move, delete operations.
"""

import shutil
import os
from pathlib import Path
from typing import Tuple, Optional
from loguru import logger

from jarvis.config.settings import ENABLE_FILE_OPERATIONS

class FileManager:
    """Manage file operations with safety checks."""
    
    def __init__(self):
        self.protected_paths = [
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\ProgramData",
            os.path.expandvars("%SystemRoot%"),
        ]
    
    def _normalize_path(self, path: str) -> Path:
        """Normalize and expand path."""
        # Expand user (~) and environment variables
        expanded = os.path.expandvars(os.path.expanduser(path))
        return Path(expanded).resolve()
    
    def _is_safe_operation(self, path: Path) -> Tuple[bool, str]:
        """Check if operation is safe (not system directory)."""
        if not ENABLE_FILE_OPERATIONS:
            return False, "File operations are disabled in settings. ⚠️"
        
        try:
            str_path = str(path).lower()
            for protected in self.protected_paths:
                if protected.lower() in str_path:
                    return False, f"Cannot operate on system directory: {path}"
            
            return True, "Safe"
        except Exception as e:
            return False, f"Path safety check failed: {e}"
    
    def copy_files(self, src: str, dst: str) -> Tuple[bool, str]:
        """
        Copy files or directories.
        
        Args:
            src: Source path
            dst: Destination path
            
        Returns:
            Tuple of (success, message)
        """
        try:
            src_path = self._normalize_path(src)
            dst_path = self._normalize_path(dst)
            
            # Safety check
            safe, msg = self._is_safe_operation(src_path)
            if not safe:
                return False, msg
            
            if not src_path.exists():
                return False, f"Source doesn't exist: {src}"
            
            # Create destination parent if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            if src_path.is_file():
                shutil.copy2(src_path, dst_path)
                logger.info(f"Copied file: {src_path} -> {dst_path}")
                return True, f"Copied file to {dst_path.name}! 📄"
            else:
                if dst_path.exists():
                    dst_path = dst_path / src_path.name
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                logger.info(f"Copied directory: {src_path} -> {dst_path}")
                return True, f"Copied folder to {dst_path.name}! 📁"
                
        except Exception as e:
            logger.error(f"Copy failed: {e}")
            return False, f"Couldn't copy: {str(e)}"
    
    def move_files(self, src: str, dst: str) -> Tuple[bool, str]:
        """
        Move files or directories.
        
        Args:
            src: Source path
            dst: Destination path
            
        Returns:
            Tuple of (success, message)
        """
        try:
            src_path = self._normalize_path(src)
            dst_path = self._normalize_path(dst)
            
            safe, msg = self._is_safe_operation(src_path)
            if not safe:
                return False, msg
            
            if not src_path.exists():
                return False, f"Source doesn't exist: {src}"
            
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dst_path))
            logger.info(f"Moved: {src_path} -> {dst_path}")
            return True, f"Moved to {dst_path.name}! 🚀"
            
        except Exception as e:
            logger.error(f"Move failed: {e}")
            return False, f"Couldn't move: {str(e)}"
    
    def delete_path(self, path: str, confirm: bool = False) -> Tuple[bool, str]:
        """
        Delete file or directory.
        
        WARNING: Requires confirmation for safety.
        
        Args:
            path: Path to delete
            confirm: Must be True to actually delete
            
        Returns:
            Tuple of (success, message)
        """
        if not confirm:
            return False, "Safety first! Please confirm deletion. 🛡️ Say 'confirm delete'"
        
        try:
            target = self._normalize_path(path)
            
            safe, msg = self._is_safe_operation(target)
            if not safe:
                return False, msg
            
            if not target.exists():
                return False, f"Path doesn't exist: {path}"
            
            if target.is_file():
                target.unlink()
                logger.info(f"Deleted file: {target}")
                return True, f"Deleted {target.name}! 🗑️"
            else:
                shutil.rmtree(target)
                logger.info(f"Deleted directory: {target}")
                return True, f"Deleted folder {target.name}! 🗑️"
                
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False, f"Couldn't delete: {str(e)}"
    
    def list_directory(self, path: str = ".") -> Tuple[bool, str]:
        """List contents of a directory."""
        try:
            target = self._normalize_path(path)
            
            if not target.exists():
                return False, f"Path doesn't exist: {path}"
            
            if not target.is_dir():
                return False, f"Not a directory: {path}"
            
            items = list(target.iterdir())
            files = [f.name for f in items if f.is_file()]
            dirs = [d.name for d in items if d.is_dir()]
            
            result = f"📁 {target.name}:\n"
            if dirs:
                result += "Folders: " + ", ".join(dirs[:10]) + ("\n..." if len(dirs) > 10 else "\n")
            if files:
                result += "Files: " + ", ".join(files[:10]) + ("..." if len(files) > 10 else "")
            
            return True, result
            
        except Exception as e:
            return False, str(e)

# Global instance
file_manager = FileManager()