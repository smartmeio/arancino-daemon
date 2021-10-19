#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import time, random, threading
import multiprocessing as mp

# client, user and device details
serverUrl   = "mqtt.cumulocity.com"
clientId    = "my_mqtt_python_client"
device_name = "My Python MQTT device"
tenant      = "<<tenant_ID>>"
username    = "<<username>>"
password    = "<<password>>"

# task queue to overcome issue with paho when using multiple threads:
#   https://github.com/eclipse/paho.mqtt.python/issues/354
task_queue = mp.Queue()

# display all incoming messages
def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    print(" < received message " + payload)
    if payload.startswith("510"):
        task_queue.put(perform_restart)

# simulate restart
def perform_restart():
    print("Simulating device restart...")
    publish("s/us", "501,c8y_Restart", wait_for_ack = True);

    print("...restarting...")
    time.sleep(1)

    publish("s/us", "503,c8y_Restart", wait_for_ack = True);
    print("...restart completed")

# send temperature measurement
def send_measurement():
    print("Sending temperature measurement...")
    temperature = random.randint(10, 20)
    publish("s/us", "211,{}".format(temperature))

# publish a message
def publish(topic, message, wait_for_ack = False):
    QoS = 2 if wait_for_ack else 0
    message_info = client.publish(topic, message, QoS)
    if wait_for_ack:
        print(" > awaiting ACK for {}".format(message_info.mid))
        message_info.wait_for_publish()
        print(" < received ACK for {}".format(message_info.mid))

# display all outgoing messages
def on_publish(client, userdata, mid):
    print(" > published message: {}".format(mid))

# main device loop
def device_loop():
    while True:
        task_queue.put(send_measurement)
        time.sleep(7)

# connect the client to Cumulocity IoT and register a device
client = mqtt.Client(clientId)
client.username_pw_set(tenant + "/" + username, password)
client.on_message = on_message
client.on_publish = on_publish

client.connect(serverUrl)
client.loop_start()
publish("s/us", "100," + device_name + ",c8y_MQTTDevice", wait_for_ack = True)
publish("s/us", "110,S123456789,MQTT test model,Rev0.1")
publish("s/us", "114,c8y_Restart")
print("Device registered successfully!")

client.subscribe("s/ds")

device_loop_thread = threading.Thread(target = device_loop)
device_loop_thread.daemon = True
device_loop_thread.start()

# process all tasks on queue
try:
    while True:
        task = task_queue.get()
        task()
except (KeyboardInterrupt, SystemExit):
    print("Received keyboard interrupt, quitting ...")
    exit(0)