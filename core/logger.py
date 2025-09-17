"""
core/logger.py - מערכת לוגים למערכת המסחר
הגדרת לוגים מרכזית עם תמיכה בקבצים וקונסול
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColorFormatter(logging.Formatter):
    """Formatter עם צבעים לקונסול"""
    
    # קודי צבעים ANSI
    COLORS = {
        'DEBUG': '\033[36m',    # ציאן
        'INFO': '\033[32m',     # ירוק
        'WARNING': '\033[33m',  # צהוב
        'ERROR': '\033[31m',    # אדום
        'CRITICAL': '\033[35m', # מגנטה
        'RESET': '\033[0m'      # איפוס
    }
    
    def format(self, record):
        """פורמט עם צבעים"""
        # שמירת הרמה המקורית
        level_name = record.levelname
        
        # הוספת צבע
        if level_name in self.COLORS:
            record.levelname = f"{self.COLORS[level_name]}{level_name}{self.COLORS['RESET']}"
        
        # פורמט רגיל
        result = super().format(record)
        
        # החזרת הרמה המקורית
        record.levelname = level_name
        
        return result


def setup_logging(
    level: str = "INFO",
    log_dir: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    max_file_size: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    הגדרת מערכת הלוגים
    
    Args:
        level: רמת לוג (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: תיקיית לוגים (ברירת מחדל: project_root/logs)
        enable_console: הצגה בקונסול
        enable_file: שמירה בקובץ
        max_file_size: גודל מקסימלי לקובץ לוג
        backup_count: מספר קבצי גיבוי
    """
    
    # קביעת תיקיית לוגים
    if log_dir is None:
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "logs"
    
    # יצירת תיקיית לוגים
    log_dir.mkdir(exist_ok=True)
    
    # הגדרת רמת לוג
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # יצירת logger ראשי
    logger = logging.getLogger("AlgoTrade")
    logger.setLevel(log_level)
    
    # מחיקת handlers קיימים (למניעת כפילויות)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # פורמט לוג
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Handler לקונסול
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # פורמטר צבעוני לקונסול
        console_formatter = ColorFormatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(console_handler)
    
    # Handler לקובץ ראשי
    if enable_file:
        log_file = log_dir / "application.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        
        # פורמטר רגיל לקובץ
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        
        logger.addHandler(file_handler)
    
    # לוגים נפרדים למסחר ושגיאות
    setup_specialized_loggers(log_dir, log_level, max_file_size, backup_count)
    
    # הודעת התחלה
    logger.info(f"Logging system initialized - Level: {level}, Dir: {log_dir}")
    
    return logger


def setup_specialized_loggers(
    log_dir: Path,
    log_level: int,
    max_file_size: int,
    backup_count: int
):
    """הגדרת לוגים מיוחדים"""
    
    # פורמט בסיסי
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)
    
    # לוג מסחר
    trading_logger = logging.getLogger("AlgoTrade.Trading")
    trading_logger.setLevel(log_level)
    
    trading_file = log_dir / "trading.log"
    trading_handler = logging.handlers.RotatingFileHandler(
        trading_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    trading_handler.setFormatter(formatter)
    trading_logger.addHandler(trading_handler)
    
    # לוג נתונים
    data_logger = logging.getLogger("AlgoTrade.Data")
    data_logger.setLevel(log_level)
    
    data_file = log_dir / "data_usage.log"
    data_handler = logging.handlers.RotatingFileHandler(
        data_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    data_handler.setFormatter(formatter)
    data_logger.addHandler(data_handler)
    
    # לוג שגיאות בלבד
    error_logger = logging.getLogger("AlgoTrade.Errors")
    error_logger.setLevel(logging.ERROR)
    
    error_file = log_dir / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_logger.addHandler(error_handler)


def get_logger(name: str = None) -> logging.Logger:
    """
    קבלת logger לפי שם
    
    Args:
        name: שם ה-logger (ברירת מחדל: AlgoTrade)
    """
    if name is None:
        return logging.getLogger("AlgoTrade")
    
    # אם השם לא מתחיל ב-AlgoTrade, נוסיף אותו
    if not name.startswith("AlgoTrade"):
        name = f"AlgoTrade.{name}"
    
    return logging.getLogger(name)


def log_trade(message: str, level: str = "INFO"):
    """לוג מסחר מיוחד"""
    logger = get_logger("Trading")
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message)


def log_data_usage(provider: str, endpoint: str, status: str, details: str = ""):
    """לוג שימוש בנתונים"""
    logger = get_logger("Data")
    message = f"Provider: {provider} | Endpoint: {endpoint} | Status: {status}"
    if details:
        message += f" | Details: {details}"
    logger.info(message)


def log_error(error: Exception, context: str = ""):
    """לוג שגיאה עם פרטים"""
    logger = get_logger("Errors")
    message = f"Error: {str(error)}"
    if context:
        message = f"Context: {context} | {message}"
    logger.error(message, exc_info=True)


class LogContext:
    """Context manager ללוגים"""
    
    def __init__(self, logger_name: str, operation: str):
        self.logger = get_logger(logger_name)
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation} | Duration: {duration}")
        else:
            self.logger.error(f"Failed: {self.operation} | Duration: {duration} | Error: {exc_val}")
        
        return False  # לא מדכא חריגות


# פונקציות עזר לשימוש מהיר
def debug(message: str, logger_name: str = None):
    """לוג debug"""
    get_logger(logger_name).debug(message)

def info(message: str, logger_name: str = None):
    """לוג info"""
    get_logger(logger_name).info(message)

def warning(message: str, logger_name: str = None):
    """לוג warning"""
    get_logger(logger_name).warning(message)

def error(message: str, logger_name: str = None):
    """לוג error"""
    get_logger(logger_name).error(message)

def critical(message: str, logger_name: str = None):
    """לוג critical"""
    get_logger(logger_name).critical(message)


logger = get_logger()
# Export
__all__ = [
    'setup_logging',
    'get_logger',
    'logger',
    'log_trade',
    'log_data_usage', 
    'log_error',
    'LogContext',
    'debug',
    'info',
    'warning',
    'error',
    'critical'
]