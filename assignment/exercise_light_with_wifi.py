import time
import machine
import network
import urequests

ssid = ""
password = ""
database_api_url = ""


ADC2 = 28

led = machine.Pin("LED", machine.Pin.OUT)
adc = machine.ADC(ADC2)

blink_period = 0.1

max_bright = 55000
min_bright = 26000

def clip(value: float) -> float:
    if value < 0:
        return 0
    if value > 1:
        return 1
    return value

def connect_wifi(ssid, password):
    print(f"Connecting to WiFi '{ssid}'...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print("Attempting to connect...")
        time.sleep(1)
    print("WiFi connected!")
    print("Network configuration:", wlan.ifconfig())

def main():
    connect_wifi(ssid, password)

    readings = []

    for i in range(10):
        value = adc.read_u16()
        readings.append(value)
        print(f"Reading {i+1}: {value}")

        duty_cycle = clip((value - min_bright) / (max_bright - min_bright))

        led.high()
        time.sleep(blink_period * duty_cycle)

        led.low()
        time.sleep(blink_period * (1 - duty_cycle))

    average_reading = sum(readings) / len(readings)
    min_reading = min(readings)
    max_reading = max(readings)

    print("\n--- Results ---")
    print(f"Average reading: {average_reading:.2f}")
    print(f"Minimum reading: {min_reading}")
    print(f"Maximum reading: {max_reading}")

    data = {
        "readings": readings,
        "average_reading": average_reading,
        "min_reading": min_reading,
        "max_reading": max_reading,
    }

    try:
        print("\nUploading data to the cloud server...")
        response = urequests.post(database_api_url, json=data)
        print(f"Server response: {response.text}")
        response.close()
    except Exception as e:
        print(f"Failed to upload data: {e}")

if __name__ == "__main__":
    main()
