
# BAUR OPC UA File Bridge

An industrial data bridge that monitors local testing machine text logs (e.g., from a BAUR breakdown tester), parses the measurement data, handles local/network file rotation, and exposes the data via an asynchronous OPC UA server interface.

## System Architecture

The application is structured using a **Separation of Concerns (SoC)** model to maximize reliability and isolate network or file system issues:

* **`config.py`**: Centralized configuration file containing paths, network endpoints, and timing variables.
* **`file_reader.py`**: Interacts with the file system. Detects new log files, parses raw strings into structured data, converts European floating-point metrics, and archives processed logs.
* **`opcua_server.py`**: Manages the live industrial protocol connection, initializes custom string Node IDs, and handles data-type variant mapping (`Double`, `Int32`, `DateTime`).
* **`main.py`**: The central orchestrator running an asynchronous event loop that ties the file reader and OPC UA server tasks together.

---

## Directory Layout

```text
BAUR_OPCUA/
│
├── .venv/                   # Python Virtual Environment
├── config.py                # Global settings and environment paths
├── file_reader.py           # Text parser and file archiver logic
├── opcua_server.py          # OPC UA Server definition & node layouts
├── main.py                  # Core runtime loop (Application Entry Point)
└── requirements.txt         # Cached environment dependencies
```


---

## Technical Specifications & Mapping

### Address Space Hierarchy

All variables are mapped under custom string Node IDs using namespace index `2` (`ns=2`) for persistent, reliable client mapping:

```text
Root
└── Objects
    └── BreakdownTester [Object]
        ├── DeviceInfo [Object]
        │   ├── Model (String)
        │   ├── FirmwareVersion (String)
        │   └── SerialNumber (String)
        ├── TestMetadata [Object]
        │   ├── SampleNumber (String)
        │   ├── ElectrodeGap_mm (Double)
        │   └── Frequency_Hz (Int32)
        └── Results [Object]
            ├── Timestamp (DateTime)
            ├── Temperature_C (Double)
            ├── Measurement_1 (Double)
            ├── Measurement_2 (Double)
            ├── Measurement_3 (Double)
            ├── Measurement_4 (Double)
            ├── Measurement_5 (Double)
            ├── Measurement_6 (Double)
            ├── Average_kV (Double)
            └── StdDeviation_kV (Double)

```

---

## Production Deployment & Installation

### Prerequisite Setup (Local Server/PC)

1. **Verify Python Installation**: Ensure Python 3.11 or 3.12 is installed on the host machine.
2. Connect PC to Fileshare or change the Paths in the config.py file
3. **Create Paths**: Verify the following target directories exist or that the execution account has full permissions to create them:
* **Source Ingestion Folder**: `C:\Users\Öldurchschlag\Desktop\BAUR_Messergebnisse\textfile`
* **Network Fileshare Destination**: `\\atlnzotfs01\Data\MF - Maschinen\MF DR – Drying\1009_OT_Messgeräte\Berichte`
* **Application Logs**: `\\atlnzotfs01\Data\MF - Maschinen\MF DR – Drying\1009_OT_Messgeräte\Logs\baur_opcua.log`



### Setup Environment & Dependencies

Open an Administrative PowerShell window in the project root folder:

```powershell
# Create the virtual environment
python -m venv .venv

# Activate the environment
.venv\Scripts\activate

# Install required components
pip install asyncua

```

---

## Running the Application

### Manual Verification Mode

To run the bridge interactively for diagnostic verification:

```powershell
.venv\Scripts\activate
python main.py

```

Open **UaExpert** and connect to the configured endpoint (`opc.tcp://localhost:4840/freeopcua/server/`) to verify node visibility.

### Unattended Production Run (Windows Task Scheduler)

To ensure the script runs 24/7 as a headless background process that survives user logoffs:

1. Open **Task Scheduler** and click **Create Task...**
2. **General Tab**:
* Select **"Run whether user is logged on or not"**
* Check **"Run with highest privileges"**


3. **Triggers Tab**: Add a new trigger set to **"At startup"**.
4. **Actions Tab**: Add a "Start a program" action:
* **Program/script**: `C:\<YOUR_PATH>\.venv\Scripts\pythonw.exe` *(Note the 'w' in pythonw.exe to suppress console windows)*
* **Add arguments**: `main.py`
* **Start in**: `C:\<YOUR_PATH>\BAUR_OPCUA` *(Crucial for relative imports)*


5. **Settings Tab**:
* **Uncheck** "Stop the task if it runs longer than 3 days".
* Set "If the task fails, restart every" to **1 minute**.
* Set "If the task is already running..." to **Do not start a new instance**.



---

## OT Hardening & Offline Compliance

If dropping this server machine into an internet-isolated or air-gapped factory VLAN:

1. **Local Dependency Caching**: Run `pip download -r requirements.txt -d .\offline_wheels` before moving offline to cache library backups locally.
2. **NTP Sync**: Ensure Windows Time Service (`w32tm`) is pointed to a valid local on-premises OT NTP time source (e.g., Firewall, Layer 3 Core Switch, or Domain Controller) to prevent tag timestamp validation drift.
3. **Static Networking**: Ensure a permanent static IP is bound, and leave the Default Gateway empty if communication outside the local plant subnet is unauthorized.

```

```
