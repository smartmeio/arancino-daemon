import logging
import paho.mqtt.client as mqtt  #import the client1
import time,sys,datetime

username="arancino-daemon"
password="d43mon"

'''def on_log(client, userdata, level, buf):
    print("log:", str(buf))

def on_disconnect(client,userdata,flags,rc=0):
    print("Disconnected flags" + " result code " + str(rc))'''

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK")
        print("cliente connesso" + str(datetime.datetime.now()))
    else:
        print("Bad connection Returned code=",rc) 
        client.bad_connection_flag=True
        

mqtt.Client.connected_flag=False #create flag in class
broker="server.smartme.io"
client = mqtt.Client()             #create new instance
client.username_pw_set(username, password) 
client.on_connect=on_connect  #bind call back function
#client.on_disconnect=on_disconnect
#client.on_log=on_log
client.loop_start()
print("Connecting to broker ",broker)
client.connect(broker)      #connect to broker

mqtt.Client.bad_connection_flag=False

while not client.connected_flag and not client.bad_connection_flag: #wait in loop
    print("In wait loop")
    time.sleep(1)
if client.bad_connection_flag:
    client.loop_stop()   #Stop loop
    sys.exit() 
    
client.loop_stop()    #Stop loop 
client.disconnect()   