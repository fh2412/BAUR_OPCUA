from pathlib import Path

# ==============================================================================
# FILE SYSTEM PATHS
# ==============================================================================
# Use raw strings (r"...") to safely handle Windows backslashes
SOURCE_DIR = Path(r"C:\Users\Öldurchschlag\Desktop\BAUR_Messergebnisse\textfile")
BACKUP_DIR = Path(r"\\atlnzotfs01\Data\MF - Maschinen\MF DR – Drying\1009_OT_Messgeräte\Berichte")
LOGS_DIR = Path(r"\\atlnzotfs01\Data\MF - Maschinen\MF DR – Drying\1009_OT_Messgeräte\Logs\baur_opcua.log") #MUST POINT TO A FILE NOT A FOLDER!!!
# ==============================================================================
# OPC UA SERVER CONFIGURATION
# ==============================================================================
# 0.0.0.0 allows the server to listen on all available network cards/IPs
OPCUA_ENDPOINT = "opc.tcp://172.24.109.2:4840"
SERVER_NAME = "Factory Breakdown Tester Bridge"
NAMESPACE_URI = "http://industrial.automation/breakdown_tester"

# ==============================================================================
# RUNTIME TIMINGS
# ==============================================================================
# How long the background loop sleeps before checking for a new text file
POLLING_INTERVAL_SECONDS = 2.0