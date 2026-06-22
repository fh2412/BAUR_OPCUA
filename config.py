from pathlib import Path

# ==============================================================================
# FILE SYSTEM PATHS
# ==============================================================================
# Use raw strings (r"...") to safely handle Windows backslashes
SOURCE_DIR = Path(r"C:\Users\Öldurchschlag\Documents\ol_testdaten")
BACKUP_DIR = Path(r"C:\Users\Öldurchschlag\Documents\ol_testdaten_backup")
# ==============================================================================
# OPC UA SERVER CONFIGURATION
# ==============================================================================
# 0.0.0.0 allows the server to listen on all available network cards/IPs
OPCUA_ENDPOINT = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
SERVER_NAME = "Factory Breakdown Tester Bridge"
NAMESPACE_URI = "http://industrial.automation/breakdown_tester"

# ==============================================================================
# RUNTIME TIMINGS
# ==============================================================================
# How long the background loop sleeps before checking for a new text file
POLLING_INTERVAL_SECONDS = 2.0