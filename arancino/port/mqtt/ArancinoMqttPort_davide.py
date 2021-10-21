import paho.mqtt.client as mqtt  #import the client1
import time,sys,datetime
import logging

logging.basicConfig(level=logging.INFO)

broker="server.smartme.io"
username="arancino-daemon"
password="d43mon"
port=1883
topic="python/mqtt"

def on_log(client, userdata, level, buf):
    logging.info(buf)

def on_disconnect(client,userdata, rc):
    logging.info("Client disconnect")

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True      #set flag
        print("Connected OK")
        print("cliente connesso " + str(datetime.datetime.now()))
    else:
        print("Bad connection Returned code=",rc) 
        client.bad_connection_flag=True
           
def on_publish(client, userdata, mid):
    logging.info("In on_pub callback mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    logging.info("Subscribed")
def on_message(client, userdata, message):
    print("message received  ",str(message.payload.decode("utf-8")), "topic",message.topic," retained ",message.retain)
    if message.retain==1:
        print("This is a retained message")


mqtt.Client.connected_flag=False
client = mqtt.Client()         #create a new istance
client.username_pw_set(username, password)  #Set a username and optionally a password for broker authentication.
client.on_log=on_log        #Called when the client has log information
client.on_connect=on_connect
client.on_disconnect=on_disconnect
client.on_publish=on_publish    #Called when a message that was to be sent using the publish() call has completed transmission to the broker.
client.on_subscribe= on_subscribe   #Called when the broker responds to a subscribe request. 
client.on_message=on_message


print("Connecting to broker ",broker)
client.connect(broker,port)

client.loop_start()

mqtt.Client.bad_connection_flag=False

while not client.connected_flag and not client.bad_connection_flag: #wait in loop
    print("In wait loop")
    time.sleep(1)
if client.bad_connection_flag:
    client.loop_stop()   #Stop loop
    sys.exit() 


logging.info("Publishing")
ret=client.publish("mqtt/python", "test message 0", 0)
logging.info("Published return=" + str(ret))
time.sleep(3)

ret=client.publish("mqtt/python", "test message 1", 1)
logging.info("Published return=" + str(ret))
time.sleep(3)

ret=client.publish("mqtt/python", "test message 2", 2)
logging.info("Published return=" + str(ret))
time.sleep(3)

logging.info("Subscribing: ")
time.sleep(3)
ret= client.subscribe(("mqtt/python", 2))
ret1=client.subscribe(("mqtt/python", 1))
logging.info("Subscribed return=" + str(ret) + str(ret1))

time.sleep(5)

client.loop_stop()
client.disconnect()
