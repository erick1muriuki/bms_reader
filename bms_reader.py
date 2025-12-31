import asyncio
import json
from zoneinfo import ZoneInfo 
from datetime import datetime
from bleak import BleakClient
import paho.mqtt.client as mqtt

# ----------------------
# Configuration
# ----------------------
BATTERIES = [
    "A4:C1:37:23:D0:5E",
    "A4:C1:37:33:D0:72",
    "A4:C1:37:23:CE:CE",
    "A4:C1:37:53:CE:E3",
]

METER_NAMES = ["BATT1", "BATT2", "BATT3", "BATT4"]

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# ----------------------
# BLE UUIDs
# ----------------------
JBD_WRITE_UUID  = "0000ff02-0000-1000-8000-00805f9b34fb"
JBD_NOTIFY_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"
READ_BASIC_INFO = bytes.fromhex("DD A5 03 00 FF FD 77")


latest_battery_data = {}


def parse_jbd_frame(buffer: bytearray):
    volts       = int.from_bytes(buffer[4:6], "big") / 100
    amps        = int.from_bytes(buffer[6:8], "big", signed=True) / 100
    watts       = volts * amps
    remain_ah   = int.from_bytes(buffer[8:10], "big") / 100
    total_ah    = int.from_bytes(buffer[10:12], "big") / 100
    soc         = int.from_bytes(buffer[12:13], "big")
    cycles      = int.from_bytes(buffer[13:15], "big")
    temps_c     = int.from_bytes(buffer[15:16], "big")
    return volts, amps, watts, remain_ah, total_ah, soc, cycles, temps_c

# ----------------------
# Read a single battery
# ----------------------
async def read_battery(mac, battery_id):
    buffer = bytearray()

    def notify(_, data):
        buffer.extend(data)

    try:
        async with BleakClient(mac, timeout=6) as client:
            await client.start_notify(JBD_NOTIFY_UUID, notify)
            await client.write_gatt_char(JBD_WRITE_UUID, READ_BASIC_INFO)
            await asyncio.sleep(0.6)  # fast notify window
            await client.stop_notify(JBD_NOTIFY_UUID)

        if len(buffer) < 16:
            return  # incomplete frame, skip

        volts, amps, watts, remain_ah, total_ah, soc, cycles, temps_c = parse_jbd_frame(buffer)

        # Store all properties in memory
        #reading_timestamp = datetime.now().isoformat()
        timestamp = datetime.now(ZoneInfo("Europe/Berlin")).isoformat()
        capacity_percent = round((remain_ah / total_ah) * 100, 1) if total_ah > 0 else 0
        latest_battery_data[battery_id] = {
            "battery_id": battery_id,
            #"timestamp": reading_timestamp,
            "timestamp": datetime.now(ZoneInfo("Europe/Berlin")).isoformat(),
            "voltage": volts,
            "current": amps,
            "power": watts,
            "capacity_remain_ah": remain_ah,
            "capacity_total_ah": total_ah,
            "capacity_percent": capacity_percent,
            "cycles": cycles,
            
        }

        #mqtt_client.publish(
                # f"bms/{battery_id}/status",
                           #  json.dumps(latest_battery_data[battery_id], indent=2, sort_keys=True)
                           # )
        mqtt_client.publish(f"bms/{battery_id}/status", json.dumps(latest_battery_data[battery_id]))

    except Exception:
        pass 

async def main():
    while True:
        for mac, name in zip(BATTERIES, METER_NAMES):
            await read_battery(mac, name)
            await asyncio.sleep(0.3)  # minimal BLE recovery

        await asyncio.sleep(2)  # refresh interval

asyncio.run(main())
