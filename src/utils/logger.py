import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = "market_maker", log_dir: str = "logs") -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        log_dir: Directory to store log files
    
    Returns:
        Configured logger instance
    """
    # สร้าง logs directory ถ้ายังไม่มี
    Path(log_dir).mkdir(exist_ok=True)
    
    # สร้าง logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # ถ้ามี handlers อยู่แล้ว ไม่ต้องเพิ่มใหม่
    if logger.handlers:
        return logger
    
    # Format สำหรับ log messages
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_file = Path(log_dir) / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

