# smartdirs
Python package to create directories with consistent naming, automatic numbering, and custom date/time formats with timezone support. 

# Installation
pip install smartdirs

# Configuration
Create a ~/.smartdirs.ini file:
[smartdirs]
timezone=America/New_York
time_format_with_seconds=true
log_dir=~/smartdirs_logs

# Usage
from smartdirs import create_dir

# Create directory with date and American time format
path = create_dir("data", use_date=True, use_time=True)
print(path)  # e.g., ./1-data-2025-05-17-8:08PM

# With seconds (if configured)
path = create_dir("results", use_date=True, use_time=True)
print(path)  # e.g., ./1-results-2025-05-17-8:08:32PM

# Custom date format and timezone
path = create_dir("output", use_date=True, date_format="%Y%m%d", timezone="Europe/Moscow")
print(path)  # e.g., ./1-output-20250517

# Log File
Logs are saved to log_dir/smartdirs.log (if configured). Example:
Date,Directory,Path
"May 17, 2025 at 8:08 AM","1-data-2025-05-17-8:08PM","/path/to/1-data-2025-05-17-8:08PM"

