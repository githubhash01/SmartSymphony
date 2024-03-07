#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  microphone2.py
#  
#  Copyright 2024  <pi@porygon>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import smbus
import time

# Define the I2C bus number (Raspberry Pi 3 and later use bus 1)
I2C_BUS = 1

# Define the I2C address of the Grove Base Hat ADC
ADC_ADDRESS = 0x04

# Function to read analog data from specified channel
def read_analog(channel):
    bus = smbus.SMBus(I2C_BUS)
    # Send command to read analog data from specified channel
    bus.write_byte(ADC_ADDRESS, channel)
    # Wait for conversion (adjust according to sensor requirements)
    time.sleep(0.1)
    # Read 2 bytes of data (12-bit ADC, so 0-4095)
    data = bus.read_word_data(ADC_ADDRESS, 0)
    # Convert data to voltage (assuming Vref is 5V)
    voltage = (data * 5.0) / 4096.0
    return voltage

try:
    while True:
        # Read analog data from Grove analog microphone connected to channel A0
        mic_voltage = read_analog(0)
        # Print the analog voltage
        print("Analog Voltage (Microphone): {:.2f} V".format(mic_voltage))
        # Optionally, perform further processing or actions based on the microphone data
        # Example: sound level analysis, triggering actions based on sound levels, etc.
        # Insert your code here
        time.sleep(1)  # Adjust the sampling interval as needed

except KeyboardInterrupt:
    print("Exiting...")

