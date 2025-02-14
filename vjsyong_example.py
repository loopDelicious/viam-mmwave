import time
import logging
from LD2410 import *

def main():
    # Initialize radar with proper baud rate and verbosity
    radar = LD2410("/dev/ttyUSB0", PARAM_BAUD_256000, verbosity=logging.INFO)

    # Get Radar Firmware version
    fw_ver = radar.read_firmware_version()
    print(f"Firmware Version: {fw_ver}")

    # Set detection parameters: moving max gate=2, static max gate=3, timeout=1s
    radar.edit_detection_params(2, 3, 1)

    # Set gate 3 moving energy sensitivity to 50, static sensitivity to 40
    radar.edit_gate_sensitivity(3, 50, 40)

    # Retrieve and print the detection parameters
    detection_params = radar.read_detection_params()
    print(f"Detection Parameters: {detection_params}")

    # Start the radar (polls asynchronously at 10Hz)
    radar.start()

    # Get 5 data frames in standard mode
    print("\n📡 Standard Mode Readings:")
    for _ in range(5):
        data = radar.get_data()
        if data and isinstance(data[0], list):
            detection_type, move_dist, move_energy, static_dist, static_energy, overall_dist = data[0]
            detection_status = {
                0: "No Target",
                1: "Moving Target",
                2: "Static Target",
                3: "Moving and Static Targets"
            }.get(detection_type, "Unknown")
            print(f"Detection: {detection_status}, Moving: {move_dist} cm (Energy: {move_energy}), "
                  f"Static: {static_dist} cm (Energy: {static_energy}), Overall: {overall_dist} cm")
        else:
            print("No valid data received.")
        time.sleep(1)

    # Enable engineering mode for detailed gate-level energy readings
    print("\n🔬 Engineering Mode Readings:")
    radar.enable_engineering_mode()

    for _ in range(5):
        eng_data = radar.get_data()
        print(f"Engineering Mode Data: {eng_data}")  # This includes gate energy levels
        time.sleep(1)

    radar.disable_engineering_mode()

    # Stop the radar
    radar.stop()
    print("\n⏹️ Radar stopped.")

    # Restart the radar
    radar.restart_module()
    print("🔄 Radar restarted.")

    # Get Bluetooth MAC address
    bt_mac = radar.bt_query_mac()
    print(f"🔵 Bluetooth MAC Address: {bt_mac}")

    # Uncomment to reset the radar to factory settings
    # radar.factory_reset()

if __name__ == "__main__":
    main()
