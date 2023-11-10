from flask import Flask, request, jsonify
import threading
import json
import math
import requests

# Import library untuk Modbus
from pyModbusTCP.client import ModbusClient

app = Flask(__name__)

# Definisikan host dan port sebagai variabel global
# HOST_CHILLER_T3_T4_T2 = '192.168.1.229'
HOST_CHILLER_T3_T4_T2 = '192.168.2.101'
# HOST_CHILLER_T1_AMP_T1_SND = '192.168.1.219'
HOST_CHILLER_T1_AMP_T1_SND = '192.168.2.102'
# PLC_CHILLER_T4 = '192.168.1.243'
PLC_CHILLER_T4 = '192.168.2.103'
# AMPERE_T2_T4 = '192.168.1.228'
AMPERE_T2_T4 = '192.168.2.104'

AMPERE_T3 = '192.168.2.105'

ARDUINO_CHILLER_SOUND = "http://192.168.2.107:80"

PORT = 502

# Daftar fungsi dan alamat register yang sesuai
FUNCTIONS = {
    "ON/OFF Setting": 0,
    "Water Inlet Temperature In Cooling Mode": 2,
    "Water Outlet Temperature Setting In Cooling Mode": 21
}
unit_fault_message = [
    "Reserved",
    "Dial switch fault",
    "RT12 sensor fault",
    "Water flow of hot water side too small fault",
    "communication fault with extension board",
    "temperature of hot water side too low",
    "Memorizer fault",
    "Water inlet/outlet temperature sensor connected reversely",
    "communication fault with master unit",
    "Ambient air temperature too high/too low fault",
    "RT8 sensor fault",
    "RT7 sensor fault",
    "RT6 sensor fault",
    "Water temperature of air-conditioning side too low fault",
    "Temperature difference between water inlet and outlet too large fault",
    "Water flow insufficiency of air-conditioning side fault"
]

system_1fault_message = [
    "Reserved",
    "System 1 discharge temperature too high",
    "VI1 sensor fault",
    "System 1Compressor2overloadfault",
    "System 1Compressor1overloadfault",
    "System 1 fan fault",
    "System 1 high pressure fault",
    "System 1 low pressure fault",
    "System 1 Refrigerant leakage fault",
    "System 1 discharge temperature too high fault",
    "System 1suction temperature too high fault",
    "System 1suction super heat too low fault",
    "RT1 sensor fault",
    "RT3 sensor fault",
    "RT9 sensor fault",
    "RT11 sensor fault"
]

system_2fault_message = [
    "Reserved",
    "System 2 discharge temperature abnormal",
    "VI2 sensor fault",
    "System 2 Compressor 2overload fault",
    "System 2Compressor1overload fault",
    "System 2fan fault",
    "System 2high pressure fault",
    "System 2low pressure fault",
    "System 2 Refrigerant leakage fault",
    "System 2 discharge temperature too high fault",
    "System 2suction temperature too high fault",
    "System 2 suction super heat too low fault",
    "RT2 sensor fault",
    "RT4 sensor fault",
    "RT10 sensor fault",
    "RT12 sensor fault"
]

system_1_2_other_fault = [
    "",
    "",
    "",
    "",
    "VI4 sensor fault",
    "VI3 sensor fault",
    "RT10 sensor fault",
    "RT4 sensor fault",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    ""
]
def decimal_to_16_bit_array(n):
    bit_array = [0] * 16  # Membuat array dengan 16 bit, diisi dengan 0
    
    for i in range(16):
        bit = n & 1
        bit_array[15 - i] = bit
        n >>= 1

    return bit_array


def display_error_messages(bit_array, alarm_array):
    if alarm_array == 0:
        alarm_messages = unit_fault_message
    elif alarm_array == 1:
        alarm_messages = system_1fault_message
    elif alarm_array == 2:
        alarm_messages = system_2fault_message
    elif alarm_array == 3:
        alarm_messages = system_1_2_other_fault
    else:
        alarm_messages = []

    error_messages = []
    
    for i, bit_value in enumerate(bit_array):
        if bit_value and i < len(alarm_messages):
            error_messages.append(alarm_messages[i])
    
    return error_messages
            
# Definisikan route atau endpoint untuk membaca data dari Modbus
@app.route('/read_input_register/<int:unit_id>', methods=['GET'])
def read_input_register(unit_id):
    try:
        if unit_id > 0 and unit_id < 7:
            client = ModbusClient(host=HOST_CHILLER_T3_T4_T2, port=PORT, unit_id=unit_id,timeout=0.5)
        elif unit_id == 7:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=2,timeout=1)
        elif unit_id == 8:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=3,timeout=1)
        elif unit_id == 9:
            response = requests.get(ARDUINO_CHILLER_SOUND)
            if response.status_code == 200:
                named_data = {}
                data = response.json()
                named_data.update({
                    "Unit Fault": 0,
                    "System 1 Fault": 0,
                    "System 2 Fault": 0,
                    "Ambient Air Temperature": 0,
                    "Water Inlet Temperature": data['suhu1'],
                    "Water Outlet Temperature": data['suhu2'],
                    "System 1 and 2 Fault": 0,
                    "Water Outlet Of Hot Water Side Temperature": 0
                })
                data_json = json.dumps(named_data)
                return jsonify({
                    "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                    "data": data_json
                })
        elif unit_id == 10:
            response = requests.get(ARDUINO_CHILLER_SOUND)
            if response.status_code == 200:
                data = response.json()
                named_data = {}
                named_data.update({
                    "Unit Fault": 0,
                    "System 1 Fault": 0,
                    "System 2 Fault": 0,
                    "Ambient Air Temperature": 0,
                    "Water Inlet Temperature": data['suhu4'],
                    "Water Outlet Temperature": data['suhu3'],
                    "System 1 and 2 Fault": 0,
                    "Water Outlet Of Hot Water Side Temperature": 0
                })
                data_json = json.dumps(named_data)
                return jsonify({
                    "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                    "data": data_json
                })
        else:
            return jsonify({
            "message": f"Error unit id",
            "data": data_json
        })
        
        # Lakukan operasi pembacaan data
        # client.write_single_register(2,120)
        result = client.read_input_registers(2000, 8)
        named_data = {}
        if result:
            print("Data yang dibaca dari perangkat Modbus:", result)
            # Menambahkan penamaan untuk setiap elemen dalam array
            unit_fault = result[0]
            system1_fault = result[1]
            system2_fault = result[2]
            system_12fault = result[6]
            
            # unit_fault = 3
            # system1_fault = 4
            # system2_fault = 10
            # system_12fault = 6
            named_data.update({
                "Unit Fault": unit_fault,
                "System 1 Fault": system1_fault,
                "System 2 Fault": system2_fault,
                "Ambient Air Temperature": result[3],
                "Water Inlet Temperature": result[4],
                "Water Outlet Temperature": result[5],
                "System 1 and 2 Fault": system_12fault,
                "Water Outlet Of Hot Water Side Temperature": result[7]
            })
            
            named_data.update({
                "Error Unit Fault": display_error_messages(decimal_to_16_bit_array(unit_fault),0),
                # "Bit Unit Fault": decimal_to_16_bit_array(1),
                
                "Error System 1 Fault": display_error_messages(decimal_to_16_bit_array(system1_fault),1),
                # "Bit System 1 Fault": decimal_to_16_bit_array(2),
                
                "Error System 2 Fault": display_error_messages(decimal_to_16_bit_array(system2_fault),2),
                # "Bit System 2 Fault": decimal_to_16_bit_array(3),
                
                "Error System 1 2 Fault": display_error_messages(decimal_to_16_bit_array(system_12fault),3),
                # "Bit System 1 2 Fault": decimal_to_16_bit_array(4),
            })
            # Mengubah data menjadi format JSON
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal
            
        result = client.read_input_registers(5001, 1)
        if result:
            print("Data yang dibaca dari perangkat Modbus:", result)
            # Menambahkan penamaan untuk setiap elemen dalam array
            
            named_data.update({
                "Water Inlet Temperature Setting In Cooling Mode": result[0],
            })
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal
        
        
        result = client.read_input_registers(5005, 1)
        if result:
            named_data.update({
                "Water Outlet Temperature Setting In Cooling Mode": result[0]
            })
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal
        
        result = client.read_input_registers(5010, 1)
        if result:
            named_data.update({
                "Compressor Output Ratio": result[0]
            })
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal

        data_json = json.dumps(named_data)
        client.close()
        return jsonify({
            "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
            "data": data_json
        })
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)})

@app.route('/read_holding_register/<int:unit_id>', methods=['GET'])
def read_holding_register(unit_id):
    try:
        if unit_id > 0 and unit_id < 7:
            client = ModbusClient(host=HOST_CHILLER_T3_T4_T2, port=PORT, unit_id=unit_id,timeout=0.5)
        elif unit_id == 7:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=2,timeout=0.5)
        elif unit_id == 8:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=3,timeout=0.5)
        elif (unit_id == 9) or (unit_id == 10):
            response = requests.get(ARDUINO_CHILLER_SOUND)
            if response.status_code == 200:
                named_data = {}
                named_data.update({
                    "ON/OFF Setting": 1,
                    "Running Mode Setting": 1,
                    "Water Inlet Temperature In Cooling Mode": 0,
                    "Water Inlet Temperature In Heating Mode": 0,
                    "Water Tank Temperature Setting": 0
                })
                data_json = json.dumps(named_data)
                return jsonify({
                    "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                    "data": data_json
                })
        else:
            return jsonify({
            "message": f"Error unit id",
            "data": data_json
        })
        
        # Lakukan operasi pembacaan data
        # client.write_single_register(2,120)
        result = client.read_holding_registers(0, 5)
        named_data = {}
        if result:
            print("Data yang dibaca dari perangkat Modbus:", result)
            # Menambahkan penamaan untuk setiap elemen dalam array
            
            named_data.update({
                "ON/OFF Setting": result[0],
                "Running Mode Setting": result[1],
                "Water Inlet Temperature In Cooling Mode": result[2],
                "Water Inlet Temperature In Heating Mode": result[3],
                "Water Tank Temperature Setting": result[4]
            })
            # Mengubah data menjadi format JSON
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal
            
        result = client.read_holding_registers(21, 2)
        if result:
            print("Data yang dibaca dari perangkat Modbus:", result)
            # Menambahkan penamaan untuk setiap elemen dalam array
            
            named_data.update({
                "Water Outlet Temperature Setting In Cooling Mode": result[0],
                "Water Outlet Temperature Setting In Heating Mode": result[1]
            })
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal
        
        data_json = json.dumps(named_data)
        client.close()
        return jsonify({
            "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
            "data": data_json
        })
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)})

@app.route('/write_holding_register/<int:unit_id>', methods=['POST'])
def write_holding_register(unit_id):
    try:
        # Ambil data dari request dalam bentuk JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "Data JSON tidak ditemukan."}), 400

        # Pastikan data JSON memiliki kunci "Function" dan "value"
        if 'Function' not in data or 'value' not in data:
            return jsonify({"error": "Data JSON harus memiliki 'Function' dan 'value'."}), 400

        function = data['Function']
        value = data['value']

        # Dapatkan alamat register yang sesuai dari daftar fungsi
        if function not in FUNCTIONS:
            return jsonify({"error": f"Fungsi '{function}' tidak valid."}), 400

        address = FUNCTIONS[function]

        # Tulis ke holding register menggunakan ModbusClient
        modbus_client = ModbusClient(host=HOST_CHILLER_T3_T4_T2, port=PORT, unit_id=unit_id,timeout=0.5)
        if not modbus_client.is_open:  # Ubah menjadi properti, bukan memanggil fungsi
            if not modbus_client.open():
                return jsonify({"error": "Tidak dapat terhubung ke perangkat Modbus."}), 500

        if not modbus_client.write_single_register(address, value):
            return jsonify({"error": "Gagal menulis ke holding register."}), 500

        modbus_client.close()

        return jsonify({
            "message": f"Berhasil menulis nilai {value} ke fungsi '{function}' pada holding register."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Definisikan route atau endpoint untuk membaca data dari Modbus
@app.route('/read_input_register_ampere/<int:unit_id>', methods=['GET'])
def read_input_register_ampere(unit_id):
    try:
        if unit_id == 1 or unit_id == 2:
            client = ModbusClient(host=AMPERE_T3, port=PORT, unit_id=unit_id,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_input_registers(0, 2)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Ampere Meter" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
        elif unit_id == 3:
            client = ModbusClient(host=AMPERE_T2_T4, port=PORT, unit_id=1,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_input_registers(0, 2)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Ampere Meter" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
        elif unit_id == 4:
            client = ModbusClient(host=AMPERE_T2_T4, port=PORT, unit_id=2,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_input_registers(0, 2)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Ampere Meter" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
        elif unit_id == 5:
            client = ModbusClient(host=AMPERE_T2_T4, port=PORT, unit_id=3,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_input_registers(0, 2)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Ampere Meter" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
        elif unit_id == 6:
            client = ModbusClient(host=AMPERE_T2_T4, port=PORT, unit_id=4,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_input_registers(0, 2)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Ampere Meter" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()            
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
        elif unit_id == 7:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=7,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_input_registers(0, 2)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Ampere Meter" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()            
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
        elif unit_id == 8:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=8,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_input_registers(0, 2)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Ampere Meter" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()            
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
            
        elif unit_id == 9:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=4,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_input_registers(0, 2)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Ampere Meter" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()            
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
        elif unit_id == 10:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=5,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_input_registers(0, 2)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Ampere Meter" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()            
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)})
    
# Definisikan route atau endpoint untuk membaca data dari Modbus
@app.route('/read_water_tank/<int:unit_id>', methods=['GET'])
def read_level_water_tank(unit_id):
    try:
        if unit_id == 3:
            client = ModbusClient(host=PLC_CHILLER_T4, port=PORT, unit_id=1,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_holding_registers(60, 10)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Water Level" : result[0]
                })
            data_json = json.dumps(named_data)
            client.close()            
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)})
    
#Definisikan route untuk pembacaan tank level oli
@app.route('/read_oil_level/<int:unit_id>', methods=['GET'])
def read_oil_level(unit_id):
    try:
        if unit_id == 3:
            client = ModbusClient(host=PLC_CHILLER_T4, port=PORT, unit_id=1,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_holding_registers(72, 10)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Oil Level" : math.floor(((result[0]/10)*965.25)/10),
                    "Data PLC Oil Level": result[0]
                })
            data_json = json.dumps(named_data)
            client.close()            
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
    except Exception as e:
        print("Error:", str(e))

#Definisikan route untuk pembacaan HP dan LP pada tiap mesin chiller
@app.route('/read_hp_lp/<int:unit_id>', methods=['GET'])
def read_hp_lp(unit_id):
    try:
        if unit_id == 3:
            client = ModbusClient(host=PLC_CHILLER_T4, port=PORT, unit_id=1,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_holding_registers(4, 10)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Data LP1" : math.floor((result[0]*0.1068)+33.2064),
                    "Data LP1 2": math.floor((result[0]/6000)*870.2),
                    "Data LP1 PLC": result[0],
                    "Data HP1" : math.floor((result[1]*0.1068)+ 33.2064),
                    "Data HP1 2": math.floor((result[1]/6000)*870.2),
                    "Data HP1 PLC": result[1],
                    
                })
            data_json = json.dumps(named_data)
            client.close()            
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
    except Exception as e:
        print("Error:", str(e))

@app.route('/read_plc_data/<int:unit_id>', methods=['GET'])
def read_plc_data(unit_id):
    try:
        if unit_id == 3:
            client = ModbusClient(host=PLC_CHILLER_T4, port=PORT, unit_id=1,timeout=0.5)
            # Lakukan operasi pembacaan data
            result = client.read_holding_registers(900, 10)
            named_data = {}
            if result:
                print("Data yang dibaca dari perangkat Modbus:", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                named_data.update({
                    "Data LP1" : math.floor((result[2]*0.1068)+33.2064),
                    "Data HP1" : math.floor((result[3]*0.1068)+ 33.2064),
                    "Water Level": result[0],
                    "Oil Level":  math.floor(((result[1]/10)*965.25)/10),
                    "PLC":"T4"
                })
            data_json = json.dumps(named_data)
            client.close()            
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID {unit_id}",
                "data": data_json
            })
    except Exception as e:
        print("Error:", str(e))
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
