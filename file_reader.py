import logging
import os
import re
import shutil
from datetime import datetime
import config

def clean_float(value_str):
    """Converts a European-formatted string (e.g., '83,9 kV') into a clean float."""
    if not value_str:
        return 0.0
    sanitized = re.sub(r"[^\d,.-]", "", value_str)
    sanitized = sanitized.replace(",", ".")
    try:
        return float(sanitized)
    except ValueError:
        return 0.0

def parse_tester_log(file_path):
    """Parses the breakdown tester log format and returns a structured dictionary."""
    data = {}
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    
    # Device Info Parsing
    model_match = re.search(r"(DTA \d+C)\s+Version:\s+([\d.]+)", content)
    if model_match:
        data["model"] = model_match.group(1)
        data["version"] = model_match.group(2)
        
    serial_match = re.search(r"Serial Number:\s+(\d+)", content)
    data["serial_number"] = serial_match.group(1) if serial_match else "Unknown"

    # Timestamp Parsing
    timestamp_match = re.search(r"(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})", content)
    if timestamp_match:
        try:
            data["timestamp"] = datetime.strptime(timestamp_match.group(1), "%d.%m.%Y %H:%M")
        except ValueError:
            data["timestamp"] = datetime.now()
    else:
        data["timestamp"] = datetime.now()

    # Metadata Parsing
    sample_match = re.search(r"Sample number:\s+(\d+)", content)
    data["sample_number"] = sample_match.group(1) if sample_match else "Unknown"

    gap_match = re.search(r"Electrode gap:\s+([\d,]+)\s*mm", content)
    data["electrode_gap_mm"] = clean_float(gap_match.group(1)) if gap_match else 0.0

    freq_match = re.search(r"Test frequency:\s+(\d+)\s*Hz", content)
    data["frequency_hz"] = int(freq_match.group(1)) if freq_match else 0

    # Results Parsing
    temp_match = re.search(r"Temperature:\s+([\d,]+)\s*°C", content)
    data["temperature_c"] = clean_float(temp_match.group(1)) if temp_match else 0.0

    for i in range(1, 7):
        meas_match = re.search(r"Measurement " + str(i) + r":\s+([\d,]+)\s*kV", content)
        data[f"measurement_{i}"] = clean_float(meas_match.group(1)) if meas_match else 0.0

    avg_match = re.search(r"Avg\. value:\s+([\d,]+)\s*kV", content)
    data["average_kv"] = clean_float(avg_match.group(1)) if avg_match else 0.0

    std_dev_match = re.search(r"Standard deviation:\s+([\d,]+)\s*kV", content)
    data["std_dev_kv"] = clean_float(std_dev_match.group(1)) if std_dev_match else 0.0

    return data

def check_and_process_file():
    """
    Checks for the oldest available .txt file. 
    Parses it and moves it cleanly to the network fileshare.
    Returns the parsed dictionary data, or None if no file is ready.
    """
    # Create directories if they dropped offline
    config.SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Grab all txt files sorted by creation time (oldest first ensures FIFO queue order)
    txt_files = sorted(config.SOURCE_DIR.glob("*.txt"), key=os.path.getctime)
    
    if not txt_files:
        return None

    target_file = txt_files[0]
    
    # OT Lock Check: Verify file is done being written to by trying to append to it
    try:
        with open(target_file, "a"):
            pass
    except IOError:
        # File is still locked by the testing machine software
        return None

    # Parse file content
    parsed_data = parse_tester_log(target_file)
    
    # Construct backup target path
    destination_path = config.BACKUP_DIR / target_file.name
    if destination_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination_path = config.BACKUP_DIR / f"{target_file.stem}_{timestamp}{target_file.suffix}"
    
    # Move file out of the processing loop folder
    try:
        shutil.move(str(target_file), str(destination_path))
        return parsed_data
    except Exception as e:
        logging.error(f"Network fileshare unreachable. Holding file locally: {e}")
        return None # Returning None ensures OPC UA variables don't update with data that hasn't been backed up yet