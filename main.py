import asyncio
import sys
from datetime import datetime
import config
import file_reader
from opcua_server import FactoryOpcuaServer
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
os.chdir(script_dir)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(r"C:\ProgramData\BAUR_OPCUA\logs\bridge.log", maxBytes=1024*1024*5, backupCount=3),
        logging.StreamHandler() # Keeps terminal output active during manual runs
    ]
)
# Usage later in code: logging.info("New Log Found!") or logging.error("Fileshare offline")


async def main():
    logging.info("==================================================")
    logging.info(f" Starting: {config.SERVER_NAME}")
    logging.info("==================================================")
    
    # Initialize the OPC UA Engine
    logging.info(f"Configuring OPC UA Engine on: {config.OPCUA_ENDPOINT}")
    server_instance = FactoryOpcuaServer()
    await server_instance.start()
    
    logging.info("OPC UA Server online and listening for clients.")
    logging.info(f"Monitoring directory: '{config.SOURCE_DIR}' for log output...\n")

    try:
        while True:
            # Check for newly dropped files via the pipeline handler
            new_data = file_reader.check_and_process_file()
            
            if new_data:
                logging.info(f"[{datetime.now().strftime('%H:%M:%S')}] New Log Found!")
                logging.info(f" -> Sample ID: {new_data['sample_number']}")
                logging.info(f" -> Avg Breakdown Voltage: {new_data['average_kv']} kV")
                
                # Update our live server variables
                await server_instance.update_node_values(new_data)
                logging.info(" -> OPC UA Live Address Space updated successfully.\n")
            
            # Prevent high CPU utilization by sleeping between directory cycles
            await asyncio.sleep(config.POLLING_INTERVAL_SECONDS)

    except asyncio.CancelledError:
        logging.warning("\nShutdown sequence triggered.")
    except KeyboardInterrupt:
        logging.warning("\nManual interface termination command received.")
    finally:
        logging.warning("Closing open server socket structures...")
        await server_instance.stop()
        logging.warning("Bridge engine completely offline.")

if __name__ == "__main__":
    # Windows specific event-loop policy configuration to prevent runtime crashes
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("\nManual interface termination command received.")
        pass