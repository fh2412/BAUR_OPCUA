import logging
from datetime import datetime
from asyncua import Server, ua
import config

# Optional: Suppress noisy asyncua debug logs in the console
logging.getLogger("asyncua").setLevel(logging.WARNING)

class FactoryOpcuaServer:
    def __init__(self):
        self.server = Server()
        self.idx = None
        # Internal dictionary to map text-file keys straight to OPC UA Node objects
        self.nodes = {}

    async def start(self):
        """Initializes the server, constructs the address space, and starts listening."""
        await self.server.init()
        self.server.set_endpoint(config.OPCUA_ENDPOINT)
        self.server.set_server_name(config.SERVER_NAME)
        
        # Register our custom manufacturing namespace URI
        self.idx = await self.server.register_namespace(config.NAMESPACE_URI)
        
        # Get the root 'Objects' folder of the server
        objects_folder = self.server.nodes.objects

        # ----------------------------------------------------------------------
        # BUILD HIERARCHY (Objects/Folders)
        # ----------------------------------------------------------------------
        # Top level device container
        tester_obj = await objects_folder.add_object(
            f"ns={self.idx};s=BreakdownTester", "BreakdownTester"
        )
        
        # Sub-folders for clean categorization
        dev_info_folder = await tester_obj.add_object(
            f"ns={self.idx};s=Tester.DeviceInfo", "DeviceInfo"
        )
        metadata_folder = await tester_obj.add_object(
            f"ns={self.idx};s=Tester.TestMetadata", "TestMetadata"
        )
        results_folder = await tester_obj.add_object(
            f"ns={self.idx};s=Tester.Results", "Results"
        )

        # ----------------------------------------------------------------------
        # DEFINE VARIABLES & EXPLICIT DATA TYPES
        # ----------------------------------------------------------------------
        # 1. Device Info
        self.nodes["model"] = await dev_info_folder.add_variable(
            f"ns={self.idx};s=Tester.DeviceInfo.Model", "Model", "Unknown"
        )
        self.nodes["version"] = await dev_info_folder.add_variable(
            f"ns={self.idx};s=Tester.DeviceInfo.FirmwareVersion", "FirmwareVersion", "Unknown"
        )
        self.nodes["serial_number"] = await dev_info_folder.add_variable(
            f"ns={self.idx};s=Tester.DeviceInfo.SerialNumber", "SerialNumber", "Unknown"
        )

        # 2. Test Metadata
        self.nodes["sample_number"] = await metadata_folder.add_variable(
            f"ns={self.idx};s=Tester.Metadata.SampleNumber", "SampleNumber", "Unknown"
        )
        self.nodes["electrode_gap_mm"] = await metadata_folder.add_variable(
            f"ns={self.idx};s=Tester.Metadata.ElectrodeGap_mm", "ElectrodeGap_mm", 0.0, ua.VariantType.Double
        )
        self.nodes["frequency_hz"] = await metadata_folder.add_variable(
            f"ns={self.idx};s=Tester.Metadata.Frequency_Hz", "Frequency_Hz", 0, ua.VariantType.Int32
        )

        # 3. Test Results
        self.nodes["timestamp"] = await results_folder.add_variable(
            f"ns={self.idx};s=Tester.Results.Timestamp", "Timestamp", datetime.utcnow()
        )
        self.nodes["temperature_c"] = await results_folder.add_variable(
            f"ns={self.idx};s=Tester.Results.Temperature_C", "Temperature_C", 0.0, ua.VariantType.Double
        )
        
        # Create individual nodes for each measurement dynamically
        for i in range(1, 7):
            self.nodes[f"measurement_{i}"] = await results_folder.add_variable(
                f"ns={self.idx};s=Tester.Results.Measurement_{i}", f"Measurement_{i}", 0.0, ua.VariantType.Double
            )

        self.nodes["average_kv"] = await results_folder.add_variable(
            f"ns={self.idx};s=Tester.Results.Average_kV", "Average_kV", 0.0, ua.VariantType.Double
        )
        self.nodes["std_dev_kv"] = await results_folder.add_variable(
            f"ns={self.idx};s=Tester.Results.StdDeviation_kV", "StdDeviation_kV", 0.0, ua.VariantType.Double
        )

        # Start the network listener task
        await self.server.start()

    async def update_node_values(self, data_dict):
        """Accepts a parsed file dictionary and pushes it safely into the address space."""
        for key, value in data_dict.items():
            if key in self.nodes:
                node = self.nodes[key]
                
                # Match strict variant typing to ensure compliance with rigid client architectures
                if key == "frequency_hz":
                    await node.write_value(int(value), ua.VariantType.Int32)
                elif key == "timestamp":
                    await node.write_value(value, ua.VariantType.DateTime)
                elif isinstance(value, float):
                    await node.write_value(float(value), ua.VariantType.Double)
                else:
                    await node.write_value(value)

    async def stop(self):
        """Gracefully closes down network socket ports."""
        await self.server.stop()