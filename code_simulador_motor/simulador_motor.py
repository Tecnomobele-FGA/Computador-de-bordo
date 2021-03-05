#!/usr/bin/env python
# coding: utf-8

import can
import ctypes
import time

###########
# Definicao de variaveis
###########

c_uint8 = ctypes.c_uint8

class run_state_bits( ctypes.BigEndianStructure ): # ctypes.LittleEndianStructure ): 
    _fields_ = [
                ("reserved1",   c_uint8, 1 ),  # asByte & 1
                ("readyfor",    c_uint8, 1 ),  # asByte & 2
                ("reserved2",   c_uint8, 1 ),  # asByte & 4
                ("reserved3",   c_uint8, 1 ),  # asByte & 8
                ("stop",        c_uint8, 1 ),  # asByte & 8
                ("brake",       c_uint8, 1 ),  # asByte & 8
                ("backward",    c_uint8, 1 ),  # asByte & 8
                ("forward",     c_uint8, 1 ),  # asByte & 8             
               ]

class run_state( ctypes.Union ):
    _anonymous_ = ("bit",)
    _fields_ = [
                ("bit",    run_state_bits ),
                ("asByte", c_uint8    )
               ]

class fault_state_bits( ctypes.BigEndianStructure ): # ctypes.LittleEndianStructure ): 
    _fields_ = [
                ("t75g",   c_uint8, 1 ),  # asByte & 1
                ("bms",    c_uint8, 1 ),  # asByte & 2
                ("overspeed",   c_uint8, 1 ),  # asByte & 4
                ("overheating",   c_uint8, 1 ),  # asByte & 8
                ("overvoltage",        c_uint8, 1 ),  # asByte & 8
                ("undervoltage",       c_uint8, 1 ),  # asByte & 8
                ("overcurrent",    c_uint8, 1 ),  # asByte & 8
                ("igbt",     c_uint8, 1 ),  # asByte & 8             
               ]

class fault_state( ctypes.Union ):
    _anonymous_ = ("bit",)
    _fields_ = [
                ("bit",    fault_state_bits ),
                ("asByte", c_uint8    )
               ]


##################
# Entrada de dados
##################

bus=can.interface.Bus(bustype='socketcan', channel='can0', bitrate=250000)

motor_id1=0x10088a9e
motor_id2=0x10098a9e


run = run_state()
run.asByte=0x0
run.stop=0
run.forward=1
run.readyfor=1

fault = fault_state()
fault.asByte=0x0
fault.bms=1

voltage=round(250/0.1)  # 0.1v/bit offset -100000 range 0~500v 
current=round(100/0.1)  # 01.A/bit offset -100000 range -500~500A
temperature =40         # 1g/bit offset 40g limit 0~100g
fault_err=0

rpm = 1000        # 1 rpm  offset:0 range 0~10000
mileage = 2000    # 0.1km/bit offset 0 range 0~30000
torque =  120     # 0.1NM/bit offset -10000 range -1000~1000

print( "run   byte  : %x"   % run.asByte)
print( "reserved1  : %i"   % run.reserved1)
print( "readyfor  : %i"   % run.readyfor)
print( "reserved2  : %i"   % run.reserved2)
print( "reserved3  : %i"   % run.reserved3)
print( "stop      : %i"   % run.stop)
print( "brake     : %i"   % run.brake)
print( "backward  : %i"   % run.backward)
print( "forward   : %i"   % run.forward)


######################
# Montagem da mensagem 
######################
for x in range(10):
    data_id1=[voltage & 0x00ff, voltage >> 8, current & 0x00ff, current >> 8, temperature, run.asByte, fault_err, fault.asByte]

    data_id2=[rpm & 0x00ff, rpm >> 8, mileage & 0x00ff, mileage >> 8, torque & 0x00ff, torque >> 8, 0xff, 0xff]

    msg=can.Message(arbitration_id = motor_id1, data=data_id1, is_extended_id=True)
    bus.send(msg)

    time.sleep(0.02)

    msg=can.Message(arbitration_id = motor_id2, data=data_id2, is_extended_id=True)
    bus.send(msg)

    time.sleep(0.020)
