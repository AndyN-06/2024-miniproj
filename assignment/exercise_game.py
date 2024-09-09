"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import json
import urequests as requests
import network


N: int = 10
sample_ms = 10.0
on_ms = 500

THINGSPEAK_API_KEY = 'S0WONAE2OJT3CEOB'
THINGSPEAK_URL = "http://api.thingspeak.com/update"

SSID = ''
PASSWORD = ''


def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print("Connecting to WiFi...")
    while not wlan.isconnected():
        time.sleep(1)
        print(".", end="")

    print("\nWiFi connected!")
    print(wlan.ifconfig())  # Print the IP address assigned


def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)


def blinker(N: int, led: Pin) -> None:
    # %% let user know game started / is over

    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)


def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file.

    Parameters
    ----------

    json_filename: str
        The name of the file to write to. This will overwrite any existing file.

    data: dict
        Dictionary data to write to the file.
    """

    with open(json_filename, "w") as f:
        json.dump(data, f)


def scorer(t: list[int | None]) -> None:
    # %% collate results
    misses = t.count(None)
    print(f"You missed the light {misses} / {len(t)} times")

    t_good = [x for x in t if x is not None]
    
    if t_good:
        minTime = min(t_good)
        maxTime = max(t_good)
        avgTime = sum(t_good) / len(t_good)
    else:
        minTime = maxTime = avgTime = None

    print(t_good)
    print(f"Min response time: {minTime} ms")
    print(f"Max response time: {maxTime} ms")
    print(f"Avg response time: {avgTime} ms")


    # add key, value to this dict to store the minimum, maximum, average response time
    # and score (non-misses / total flashes) i.e. the score a floating point number
    # is in range [0..1]
    data = {
        "min_response_time": minTime,
        "max_response_time": maxTime,
        "avg_response_time": avgTime,
        "misses": misses,
        "total_flashes": len(t)
    }

    return data
    # %% make dynamic filename and write JSON

    now: tuple[int] = time.localtime()

    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"score-{now_str}.json"

    print("write", filename)

    write_json(filename, data)

def upload_thingspeak(data: dict) -> None:
    field_data = {
        'api_key': THINGSPEAK_API_KEY,
        'field1': data["min_response_time"],
        'field2': data["max_response_time"],
        'field3': data["avg_response_time"],
        'field4': data["misses"],
        'field5': data["total_flashes"]
    }
    
    response = requests.get(THINGSPEAK_URL, params=field_data)
    print(response.text)

if __name__ == "__main__":
    # using "if __name__" allows us to reuse functions in other script files
    connect_to_wifi(SSID, PASSWORD)
    

    led = Pin("LED", Pin.OUT)
    button = Pin(16, Pin.IN, Pin.PULL_UP)

    t: list[int | None] = []

    blinker(3, led)

    for i in range(N):
        time.sleep(random_time_interval(0.5, 3.0))

        led.high()

        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        t.append(t0)

        led.low()

    blinker(5, led)

    result = scorer(t)
    
    upload_thingspeak(result)
