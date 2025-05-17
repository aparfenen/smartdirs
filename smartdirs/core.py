from pathlib import Path
from datetime import datetime
import re
import pytz
from tzlocal import get_localzone
import configparser
import csv
import os

def load_config(config_file: str | Path | None = None) -> dict:
    """Load configuration from smartdirs.ini or return default settings."""
    config = {
        "timezone": None,
        "time_format_with_seconds": False,
        "log_dir": None
    }

    if config_file is None:
        config_file = Path.home() / ".smartdirs.ini"
    
    if Path(config_file).exists():
        cfg = configparser.ConfigParser()
        cfg.read(config_file)
        if "smartdirs" in cfg:
            config["timezone"] = cfg["smartdirs"].get("timezone", None)
            config["time_format_with_seconds"] = cfg["smartdirs"].getboolean(
                "time_format_with_seconds", False
            )
            config["log_dir"] = cfg["smartdirs"].get("log_dir", None)
    
    return config

def log_directory(log_dir: str | Path | None, dir_path: Path, tz) -> None:
    """Log created directory to a CSV file in a macOS-style table."""
    if not log_dir:
        return
    
    log_dir = Path(log_dir).expanduser()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "smartdirs.log"
    
    # macOS-style date: "May 17, 2025 at 8:08 AM"
    creation_time = datetime.now(tz).strftime("%b %d, %Y at %I:%M %p").replace(" 0", " ")
    
    # Prepare log entry
    headers = ["Date", "Directory", "Path"]
    row = [creation_time, dir_path.name, str(dir_path.absolute())]
    
    # Write to CSV
    file_exists = log_file.exists()
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)

def create_dir(
    base_name: str,
    parent_dir: str | Path = ".",
    use_date: bool = False,
    use_time: bool = False,
    date_format: str = "%Y-%m-%d",
    time_format: str | None = None,
    timezone: str | None = None,
    config_file: str | Path | None = None,
    prefix: bool = True,
    suffix: bool = False,
    separator: str = "-"
) -> Path:
    """
    Creates a directory with a consistent name, adding numeric prefix/suffix or date/time.
    Logs creation to a CSV file if configured.
    
    Args:
        base_name: Base name for the directory (e.g., 'data').
        parent_dir: Parent directory path (default: current directory).
        use_date: Add date to the name (default: False).
        use_time: Add time to the name (default: False).
        date_format: Custom format for date (e.g., '%Y%m%d') (default: '%Y-%m-%d').
        time_format: Custom format for time (e.g., '%I:%M%p'). If None, uses config or default.
        timezone: Timezone name (e.g., 'America/New_York'). If None, uses config or local.
        config_file: Path to config file. If None, tries ~/.smartdirs.ini or defaults.
        prefix: Add incremental number as prefix (e.g., '1-') (default: True).
        suffix: Add incremental number as suffix (e.g., '-1') (default: False).
        separator: Separator for name parts (default: '-').

    Returns:
        Path object of the created directory.

    Raises:
        pytz.exceptions.UnknownTimeZoneError: If timezone is invalid.
    """
    # Load configuration
    config = load_config(config_file)
    
    # Set timezone
    if timezone:
        tz = pytz.timezone(timezone)
    elif config["timezone"]:
        tz = pytz.timezone(config["timezone"])
    else:
        tz = get_localzone()

    # Set time format (American style: 5:45PM or 5:45:32PM)
    if time_format is None:
        time_format = "%I:%M:%S%p" if config["time_format_with_seconds"] else "%I:%M%p"

    # Create parent directory
    parent_path = Path(parent_dir)
    parent_path.mkdir(parents=True, exist_ok=True)

    # Prepare timestamp if needed
    timestamp = ""
    if use_date or use_time:
        now = datetime.now(tz)
        date_str = now.strftime(date_format) if use_date else ""
        time_str = now.strftime(time_format).lstrip("0") if use_time else ""
        timestamp = separator.join([s for s in [date_str, time_str] if s])

    # Base name for checking existing dirs
    dir_base = separator.join([s for s in [base_name, timestamp] if s])

    # Get existing directories
    existing_dirs = [d.name for d in parent_path.iterdir() if d.is_dir()]

    # Find matching directories with numeric prefix/suffix
    pattern = rf"^(?:(\d+){separator})?{re.escape(dir_base)}(?:{separator}(\d+))?$"
    max_prefix = 0
    max_suffix = 0
    for dir_name in existing_dirs:
        match = re.match(pattern, dir_name)
        if match:
            prefix_num = int(match.group(1) or 0)
            suffix_num = int(match.group(2) or 0)
            max_prefix = max(max_prefix, prefix_num)
            max_suffix = max(max_suffix, suffix_num)

    # Decide on new directory name
    if prefix and not suffix:
        new_num = max_prefix + 1
        new_dir_name = f"{new_num}{separator}{dir_base}"
    elif suffix and not prefix:
        new_num = max_suffix + 1
        new_dir_name = f"{dir_base}{separator}{new_num}"
    elif prefix and suffix:
        new_num = max(max_prefix, max_suffix) + 1
        new_dir_name = f"{new_num}{separator}{dir_base}{separator}{new_num}"
    else:
        new_dir_name = dir_base

    # Create the directory
    new_dir_path = parent_path / new_dir_name
    new_dir_path.mkdir(parents=True, exist_ok=True)

    # Log the creation
    log_directory(config["log_dir"], new_dir_path, tz)

    return new_dir_path