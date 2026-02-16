import sys
from loguru import logger
from pathlib import Path

# 1. Define where logs will be saved
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 2. Configure the logger
# We remove the default handler to set up our own custom style
logger.remove()

# Add Console Output (Colorful and readable for your terminal)
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Add File Output (Saves all logs to a file so you can check them later)
logger.add(
    LOG_DIR / "app.log",
    rotation="10 MB",     # Create a new file when it hits 10MB
    retention="10 days",   # Keep logs for 10 days
    level="DEBUG",
    compression="zip"      # Zip old logs to save space
)

# Now, any file can use 'from utils.logger import logger'