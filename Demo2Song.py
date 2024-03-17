import RPi.GPIO as GPIO
import time
import threading  # 导入线程库
import asyncio
from timeline import parseMidi

GPIO.setmode(GPIO.BCM)  # 设置GPIO编号模式为BCM

class Actuators:
    
    def __init__(self):
        self.motorPins = [12, 5, 16, 18, 22, 24, 26]
        for pin in motorPins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    
    async def play(self, midi_file, speed):
        print("WTF")
        timeline = parseMidi(midi_file)
        for event_time, wait, event in timeline:
            print(event_time, wait, 'ON' if event.event_type else 'OFF', event.key.note, event.key.led_num)
            print(event.key.actuator)
            if event.key.actuator:
                if event.event_type == 1:
                    GPIO.output(event.key.actuator, GPIO.HIGH)
                else:
                    GPIO.output(event.key.actuator, GPIO.LOW)
            
            await asyncio.sleep(wait / (speed * 1000))

# 定义连接到直线电机的GPIO引脚
motorPins = [12, 5, 16, 18,22,24,26]

# 全局变量，跟踪按键状态
notePressed = False

# 初始化GPIO引脚
def setupGPIO():
    for pin in motorPins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

# 单个电机运行函数
def motorRunner(infSet):
    GPIO.output(infSet[0], GPIO.HIGH)
    time.sleep(infSet[1])
    GPIO.output(infSet[0], GPIO.LOW)
    time.sleep(infSet[2])
#Do:12 Re:5 Mi:16 Fa:18 So:22 La:24 Si:26
Joy=[[16,0.45,0.05],[16,0.5,0],[18,0.5,0],[22,0.45,0.05],[22,0.5,0],[18,0.5,0],[16,0.5,0],[5,0.5,0],[12,0.4,0.1],[12,0.5,0],[5,0.5,0],[16,0.45,0.05],[16,0.75,0],[5,0.24,0.01],[5,1,0],[16,0.45,0.05],[16,0.5,0],[18,0.5,0],[22,0.45,0.05],[22,0.5,0],[18,0.5,0],[16,0.5,0],[5,0.5,0],[12,0.4,0.1],[12,0.5,0],[5,0.5,0],[16,0.5,0],[5,0.75,0],[12,0.24,0.01],[12,1,0]]

Do=[[12,0.25,0.1],[12,0.5,0],[5,0.25,0.1],[5,0.5,0],[16,0.25,0.1],[16,0.5,0],[18,0.25,0.1],[18,0.5,0],[22,0.25,0.1],[22,0.5,0],[24,0.25,0.1],[24,0.5,0],[26,0.25,0.1],[26,0.5,0]]

Demo=[[12,0.25,0.1],[12,0.5,0],[5,0.25,0.1],[5,0.5,0],[16,0.25,0.1],[16,0.5,0],[18,0.25,0.1],[18,0.5,0],[22,0.25,0.1],[22,0.5,0],[24,0.25,0.1],[24,0.5,0],[26,0.25,0.1],[26,0.5,0],[16,0.45,0.05],[16,0.5,0],[18,0.5,0],[22,0.45,0.05],[22,0.5,0],[18,0.5,0],[16,0.5,0],[5,0.5,0],[12,0.4,0.1],[12,0.5,0],[5,0.5,0],[16,0.45,0.05],[16,0.75,0],[5,0.24,0.01],[5,1,0],[16,0.45,0.05],[16,0.5,0],[18,0.5,0],[22,0.45,0.05],[22,0.5,0],[18,0.5,0],[16,0.5,0],[5,0.5,0],[12,0.4,0.1],[12,0.5,0],[5,0.5,0],[16,0.5,0],[5,0.75,0],[12,0.24,0.01],[12,1,0]]


# 主程序
if __name__ == "__main__":
    setupGPIO()

    try:
        for infset in Joy:
            if not notePressed:
                notePressed = True  # 更新按键状态
                # 同时激活所有电机
                motorRunner(infset)  # 例如，激活前两个电机
                 # 休息一段时间后再次检查
                notePressed = False  # 重置按键状态，准备下一次激活



    except KeyboardInterrupt:
        GPIO.cleanup()  # 清理GPIO设置