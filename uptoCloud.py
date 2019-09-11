from machine import Pin
from umqtt.simple import MQTTClient
from machine import Timer
import network
import time
import dht
import machine
import json
import ubinascii

def blinkLED(count,delayTime):
    pin0 = Pin(16,Pin.OUT)
    for i in range(count):
        pin0.value(0) #Low to enable LED
        time.sleep_ms(delayTime)
        pin0.value(1)
        time.sleep_ms(50)
        pin0.value(0)
        time.sleep_ms(delayTime)
        pin0.value(1)
    
def connectWlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Now connecting")
        wlan.connect('LXG_2.4G','61412@NETWORK')
        while not wlan.isconnected():
            pass
        print("network config:",wlan.ifconfig())
        blinkLED(1,200)
        
class getSensor_DHT11:
    sensor = dht.DHT11(Pin(4))
    
    def get_T():
        sensor = dht.DHT11(Pin(4))
        sensor.measure()    #update data
        T = sensor.temperature()
        blinkLED(2,200)
        return T
        
    def get_H():    
        sensor = dht.DHT11(Pin(4))
        sensor.measure()    #update data
        H = sensor.humidity()
        #print("Temperature:",T,"C","Humidity:",H,"%")
        blinkLED(2,200)
        return H

def OneNET_recv(_msg):pass
_OneNET_msg_list = []

def OneNET_callback(_topic, _msg):
    global _OneNET_msg_list
    try: _msg = _msg.decode('utf-8', 'ignore')
    except: print(_msg);return
    OneNET_recv(_msg)
    if _msg in _OneNET_msg_list:
        eval('OneNET_recv_' + bytes.decode(ubinascii.hexlify(_msg)) + '()')

tim14 = Timer(14)

_iot_count = 0
def timer14_tick(_):
    global _iot, _iot_count
    _iot_count = _iot_count + 1
    if _iot_count == 1000: _iot.ping(); _iot_count = 0
    try: _iot.check_msg()
    except: machine.reset()

_iot = None
def OneNET_setup():
    global _iot
    _iot = MQTTClient("543435527", "218.201.45.2", 6002, "273400", "9bWiKNlLE5WqFHPdExb=RUOJdic=", keepalive=300)
    _iot.set_callback(OneNET_callback)
    if 1 == _iot.connect(): print('Successfully connected to MQTT server.')
    tim14.init(period=200, mode=Timer.PERIODIC, callback=timer14_tick)
def pubdata(_dic):
    print(_dic)
    _list = []
    for _key in list(_dic.keys()):
        _d = {'id':_key,'datapoints':[{'value':_dic[_key]}]}
        _list.append(_d)
    _data = {'datastreams': _list}
    j_d = json.dumps(_data)
    j_l = len(j_d)
    arr = bytearray(j_l + 3)
    arr[0] = 1
    arr[1] = int(j_l / 256)
    arr[2] = j_l % 256
    arr[3:] = j_d.encode('ascii')
    return arr
    
def OneNET_recv(_msg):
    if _msg.isalpha():
        blinkLED(3,200)
        
def main():
    connectWlan()
    getSensor_DHT11()
    OneNET_setup()
    running = True
    while running:
        print("Temperature:",getSensor_DHT11.get_T(),"C")
        print("Humidity:",getSensor_DHT11.get_H(),"%")
        _iot.publish('$dp', pubdata({"Temperature":getSensor_DHT11.get_T()}))
        _iot.publish('$dp', pubdata({"Humidity":getSensor_DHT11.get_H()}))
        time.sleep(3)
        
if __name__ == "__main__":
    main()
#tim14.deinit()
#_iot.disconnect()
#print('Disconnected from MQTT server.')