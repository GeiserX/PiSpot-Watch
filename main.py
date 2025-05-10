#!/usr/bin/python3
import RPi.GPIO as GPIO
import requests
from papirus import PapirusImage
from papirus import PapirusTextPos
from papirus import PapirusText
import json
import time
import os
from datetime import datetime
import sys
import hvac
import logging
import logging.handlers

def click(pressed_channel):
    for channel in channels:
        GPIO.remove_event_detect(channel)
    logging.info("Switch " + str(switches.index(pressed_channel) + 1) + " pressed")

    try:
        client = hvac.Client(url = os.environ['VAULT_ADDR'], token = os.environ['VAULT_TOKEN'])
        client.secrets.kv.default_kv_version = "1"
        vault_response = client.secrets.kv.read_secret(mount_point = 'pispot_voucher', path = os.uname()[1])
    except Exception as e:
        for channel in channels:
            try:
                GPIO.add_event_detect(channel, GPIO.RISING, callback=click, bouncetime=200)
            except RuntimeError as ex:
                logging.exception(repr(ex))

        typeException = type(e).__name__
        logging.exception(e)
        sys.stdout.flush()
        text = PapirusText(rotation = rot)
        text.write(typeException)
        time.sleep(5)

        image = PapirusImage(rotation = rot)
        image.write(wd + '/logoGPConnect.png')

        return

    duration="0"
    if pressed_channel==21: os.system('sudo reboot'); return
    #elif pressed_channel==16: duration=""
    elif pressed_channel==20: duration=vault_response['data']['button_2'] # SW3
    elif pressed_channel==19: duration=vault_response['data']['button_3'] # SW4
    elif pressed_channel==26: duration=vault_response['data']['button_4'] # SW5

    plural = ""
    if duration != 1:
        plural = "s"

    duration_type="0"
    if vault_response['data']['duration_type']==1: duration_type = "minute"
    elif vault_response['data']['duration_type']==2: duration_type = "hour"
    elif vault_response['data']['duration_type']==3: duration_type = "day"

    tokenSpotipo = vault_response['data']['spotipo_key']

    spotipoURL = os.environ['SPOTIPO_URL'] #'https://access.your-net.us/s/X/api/voucher/create/'
    spotipoFullURL = spotipoURL + '/s/' + str(vault_response['data']['site_number']) + '/api/voucher/create/'
    headers = {"Content-Type":"application/json", "Authentication-Token":tokenSpotipo}

    try:
        r = requests.post(spotipoFullURL, headers=headers, data = json.dumps({
        "duration_val": duration,
        "duration_type": vault_response['data']['duration_type'],
        "batchid": vault_response['data']['batchid'],
        "number":  vault_response['data']['number'],
        "num_devices": vault_response['data']['num_devices'],
        "speed_dl":  vault_response['data']['speed_dl'],
        "speed_ul":  vault_response['data']['speed_ul'],
        "bytes_t":  vault_response['data']['bytes_t'],
        "notes": vault_response['data']['notes']
        }))

        rJSON = json.loads(r.text)
        voucher = rJSON['data']['vouchers'][0]

        text = PapirusTextPos(False, rotation = rot)
        text.AddText("Duration: " + str(duration) + " " + duration_type + plural, 10, 10, size=18, Id="Top")
        text.AddText(voucher, 10, 50, size=34, Id="Bottom")
        text.WriteAll()

        time.sleep(30) ## Wait for 30 secs to display the voucher code

        image = PapirusImage(rotation = rot)
        image.write(wd + '/logoGPConnect.png')
        logging.info("PaPiRus screen flushed")

    except Exception as e:
        typeException = type(e).__name__
        logging.exception(repr(e))
        text = PapirusText(rotation = rot)
        text.write(typeException)
        time.sleep(5)

        image = PapirusImage(rotation = rot)
        image.write(wd + '/logoGPConnect.png')

        return

    finally: # We guarantee this chunk of code to run even if an exceptions rises up
        for channel in channels:
            try:
                GPIO.add_event_detect(channel, GPIO.RISING, callback=click, bouncetime=200)
            except RuntimeError as ex:
                logging.exception(repr(ex))

    return

def main():
    global LOG_FILENAME
    LOG_FILENAME = "/var/log/pispot/main.log"

    handler = logging.handlers.RotatingFileHandler(filename=LOG_FILENAME, maxBytes=2000, backupCount=5)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S'))

    my_logger = logging.getLogger()
    my_logger.setLevel(logging.INFO)
    my_logger.addHandler(handler)

    now = datetime.now()
    logging.info("Python3 script started at " + now.strftime("%Y-%m-%d %H:%M:%S"))

    global rot
    global switches
    global wd
    global channels

    rot = 0
    switches = [21, 16, 20, 19, 26] # The list of the switches ordered by Switch Number
    wd = os.path.dirname(os.path.realpath(__file__))

    image = PapirusImage(rotation = rot)
    image.write(wd + '/logoGPConnect.png')

    GPIO.setmode(GPIO.BCM)
    channels=[19, 20, 21, 26] # BCM19 - SW4, BCM20 - SW3, BCM21 - SW1, BCM26 - SW5
    GPIO.setup(channels, GPIO.IN)

    for channel in channels:
        GPIO.add_event_detect(channel, GPIO.FALLING, callback=click, bouncetime=200)

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
