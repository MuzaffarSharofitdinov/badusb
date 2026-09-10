# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support


import supervisor


import time
import digitalio
from board import *
import board
from duckyinpython import *
if(board.board_id == 'raspberry_pi_pico_w'):
    import wifi
    from webapp import *


time.sleep(.5)

def startWiFi():
    import ipaddress

    print("Connect wifi")
    # ADDED: guard against calling start_ap() when an AP is already active.
    # On some CircuitPython/CYW43 (Pico W) combinations, start_ap() internally
    # tries to stop any existing AP first, and that raises:
    #   NotImplementedError: Stopping AP is not supported.
    # This happens e.g. after a soft-reload (Ctrl+D) if the radio still
    # remembers the previous AP session. Skipping the call when already
    # active avoids the crash.
    try:
        already_active = wifi.radio.ap_active
    except AttributeError:
        already_active = False

    if already_active:
        print("AP already active, skipping start_ap")
    else:
        wifi.radio.start_ap('BadUSBWiFi', '12345678')

    HOST = repr(wifi.radio.ipv4_address_ap)
    PORT = 80        # Port to listen on
    print(HOST,PORT)


supervisor.runtime.autoreload = False

if(board.board_id == 'raspberry_pi_pico'):
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
elif(board.board_id == 'raspberry_pi_pico_w'):
    led = digitalio.DigitalInOut(board.LED)
    led.switch_to_output()


progStatus = False
progStatus = getProgrammingStatus()
print("progStatus", progStatus)
if(progStatus == False):
    print("Finding payload")
    # not in setup mode, inject the payload
    payload = selectPayload()
    print("Running ", payload)
    runScript(payload)

    print("Done")
else:
    print("Update your payload")

led_state = False

async def main_loop():
    global led,button1

    button_task = asyncio.create_task(monitor_buttons(button1))
    if(board.board_id == 'raspberry_pi_pico_w'):
        pico_led_task = asyncio.create_task(blink_pico_w_led(led))
        print("Starting Wifi")
        startWiFi()
        print("Starting Web Service")
        webservice_task = asyncio.create_task(startWebService())
        await asyncio.gather(pico_led_task, button_task, webservice_task)
    else:
        pico_led_task = asyncio.create_task(blink_pico_led(led))
        await asyncio.gather(pico_led_task, button_task)

asyncio.run(main_loop())
