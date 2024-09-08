#!/usr/bin/env python3
"""
PWM Tone Generator

based on https://www.coderdojotc.org/micropython/sound/04-play-scale/
"""

import machine
import utime

# GP16 is the speaker pin
SPEAKER_PIN = 16

# create a Pulse Width Modulation Object on this pin
speaker = machine.PWM(machine.Pin(SPEAKER_PIN))


def playtone(frequency: float, duration: float) -> None:
    if frequency == 0:
        quiet()
    else:
        speaker.duty_u16(1000)
        speaker.freq(int(frequency))
    utime.sleep(duration)
    quiet()


def quiet():
    speaker.duty_u16(0)


NOTES = {
    'C4': 261, 'D4': 294, 'E4': 329, 'R': 0
}

MELODY = [
    ('E4', 0.5), ('D4', 0.5), ('C4', 0.5),
    ('E4', 0.5), ('D4', 0.5), ('C4', 0.5),
    ('C4', 0.25), ('C4', 0.25), ('C4', 0.25), ('C4', 0.25),
    ('D4', 0.25), ('D4', 0.25), ('D4', 0.25), ('D4', 0.25),
    ('E4', 0.5), ('D4', 0.5), ('C4', 0.5)
]

print("Playing 'Hot Cross Buns':")

for note, duration in MELODY:
    frequency = NOTES[note]
    print(f"Playing note: {note} ({frequency} Hz) for {duration} seconds")
    playtone(frequency, duration)

# Turn off the PWM
quiet()
