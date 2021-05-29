import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = 'your side'
password = 'your password'
mqtt_server = 'your mqtt IP adddress' # Replace with the IP or URI of the MQTT server you use
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'flag' # This is the topic you want to subscribe to
topic_pub = b'hello' # This is the topic you want to publish to
servo_pin = machine.PWM(machine.Pin(4))

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())




def sub_cb(topic, msg):
    print((topic, msg))
    if topic == b'notification' and msg == b'received':
        print('ESP received hello message')
    if topic == b'flag':
        print("move flag",msg)
        move_flag(msg)
        

def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

def restart_reconnect():
    print('Failed toconnect to MQTT broker, Reconnecting...')
    time.sleep(10)
    machine.reset()
    
def map(x, in_min, in_max, out_min, out_max):
    return int((x-in_min) * (out_max-out_min) / (in_max - in_min) + out_min)

def move_flag(angle):
    pulse = map(int(angle), in_min=0 , in_max=180,out_min=10, out_max=1000)
    servo_pin.duty(pulse)

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()
    
while True:
    try:
        client.check_msg()
        if (time.time() - last_message) > message_interval:
            msg = b'Hello #%d' % counter
            client.publish(topic_pub, msg)
            last_message = time.time()
            counter += 1
    except OSError as e:
        restart_and_reconnect()
