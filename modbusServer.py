from flask import Flask, request, jsonify
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
# PLC_CHILLER_T2 = '192.168.1.243'
PLC_CHILLER_T2 = '192.168.2.103'
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

# Definisikan route atau endpoint untuk membaca data dari Modbus
@app.route('/read_input_register/<int:unit_id>', methods=['GET'])
def read_input_register(unit_id):
    try:
        if unit_id > 0 and unit_id < 7:
            client = ModbusClient(host=HOST_CHILLER_T3_T4_T2, port=PORT, unit_id=unit_id)
        elif unit_id == 7:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=2)
        elif unit_id == 8:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=3)
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
            
            named_data.update({
                "Unit Fault": result[0],
                "System 1 Fault": result[1],
                "System 2 Fault": result[2],
                "Ambient Air Temperature": result[3],
                "Water Inlet Temperature": result[4],
                "Water Outlet Temperature": result[5],
                "System 1 and 2 Fault": result[6],
                "Water Outlet Of Hot Water Side Temperature": result[7]
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
            client = ModbusClient(host=HOST_CHILLER_T3_T4_T2, port=PORT, unit_id=unit_id)
        elif unit_id == 7:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=2)
        elif unit_id == 8:
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=3)
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
        modbus_client = ModbusClient(host=HOST_CHILLER_T3_T4_T2, port=PORT, unit_id=unit_id)
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
            client = ModbusClient(host=AMPERE_T3, port=PORT, unit_id=unit_id)
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
            client = ModbusClient(host=AMPERE_T2_T4, port=PORT, unit_id=1)
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
            client = ModbusClient(host=AMPERE_T2_T4, port=PORT, unit_id=2)
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
            client = ModbusClient(host=AMPERE_T2_T4, port=PORT, unit_id=3)
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
            client = ModbusClient(host=AMPERE_T2_T4, port=PORT, unit_id=4)
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
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=4)
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
            client = ModbusClient(host=HOST_CHILLER_T1_AMP_T1_SND, port=PORT, unit_id=5)
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
            client = ModbusClient(host=PLC_CHILLER_T2, port=PORT, unit_id=1)
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
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
