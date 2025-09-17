#!/usr/bin/env python3
"""
clear_cache.py - ניקוי כל קבצי ה-cache של Python
"""

import os
import shutil
from pathlib import Path

def clear_python_cache(root_dir="."):
    """ניקוי כל קבצי __pycache__ ו .pyc"""
    root_path = Path(root_dir)
    
    cache_dirs = []
    pyc_files = []
    
    # חיפוש כל התיקיות __pycache__
    for path in root_path.rglob("__pycache__"):
        if path.is_dir():
            cache_dirs.append(path)
    
    # חיפוש כל קבצי .pyc
    for path in root_path.rglob("*.pyc"):
        if path.is_file():
            pyc_files.append(path)
    
    # מחיקת תיקיות cache
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Deleted cache dir: {cache_dir}")
        except Exception as e:
            print(f"❌ Failed to delete {cache_dir}: {e}")
    
    # מחיקת קבצי .pyc
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            print(f"✅ Deleted .pyc file: {pyc_file}")
        except Exception as e:
            print(f"❌ Failed to delete {pyc_file}: {e}")
    
    print(f"\n🎯 Summary:")
    print(f"   Cache directories deleted: {len(cache_dirs)}")
    print(f"   .pyc files deleted: {len(pyc_files)}")
    print(f"   Cache cleared! 🚀")

if __name__ == "__main__":
    clear_python_cache()