import asyncio
import sys
from datetime import datetime
import config
import file_reader
from opcua_server import FactoryOpcuaServer

async def main():
    print("==================================================")
    print(f" Starting: {config.SERVER_NAME}")
    print("==================================================")
    
    # Initialize the OPC UA Engine
    print(f"Configuring OPC UA Engine on: {config.OPCUA_ENDPOINT}")
    server_instance = FactoryOpcuaServer()
    await server_instance.start()
    
    print("OPC UA Server online and listening for clients.")
    print(f"Monitoring directory: '{config.SOURCE_DIR}' for log output...\n")

    try:
        while True:
            # Check for newly dropped files via the pipeline handler
            new_data = file_reader.check_and_process_file()
            
            if new_data:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] New Log Found!")
                print(f" -> Sample ID: {new_data['sample_number']}")
                print(f" -> Avg Breakdown Voltage: {new_data['average_kv']} kV")
                
                # Update our live server variables
                await server_instance.update_node_values(new_data)
                print(" -> OPC UA Live Address Space updated successfully.\n")
            
            # Prevent high CPU utilization by sleeping between directory cycles
            await asyncio.sleep(config.POLLING_INTERVAL_SECONDS)

    except asyncio.CancelledError:
        print("\nShutdown sequence triggered.")
    except KeyboardInterrupt:
        print("\nManual interface termination command received.")
    finally:
        print("Closing open server socket structures...")
        await server_instance.stop()
        print("Bridge engine completely offline.")

if __name__ == "__main__":
    # Windows specific event-loop policy configuration to prevent runtime crashes
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass