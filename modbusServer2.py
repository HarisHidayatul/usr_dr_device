from flask import Flask, request, jsonify
import json
import math
import requests

# Import library untuk Modbus
from pyModbusTCP.client import ModbusClient

app = Flask(__name__)

# Definisikan IP akses untuk masing 
HOST_CHILLER_T3_T4_T2 = '192.168.2.101'
HOST_CHILLER_T1_AMP_T1_SND = '192.168.2.102'
PLC_CHILLER_T4 = '192.168.2.103'
AMPERE_T2_T4 = '192.168.2.104'
AMPERE_T3 = '192.168.2.105'
ARDUINO_CHILLER_SOUND = "http://192.168.2.107:80"