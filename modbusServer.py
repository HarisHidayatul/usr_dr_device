from flask import Flask, request, jsonify
import json
import math

# Import library untuk Modbus
from pyModbusTCP.client import ModbusClient

app = Flask(__name__)

# Definisikan host dan port sebagai variabel global
HOST = '192.168.1.229'
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
        client = ModbusClient(host=HOST, port=PORT, unit_id=unit_id)
        
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
        client = ModbusClient(host=HOST, port=PORT, unit_id=unit_id)
        
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
        modbus_client = ModbusClient(host=HOST, port=PORT, unit_id=unit_id)
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
    
@app.route('/read_pressure/<int:unit_id>', methods=['GET'])
def read_holding_pressure_register(unit_id):
    try:
        named_data = {}
        if unit_id == 1:
            client = ModbusClient(host=HOST, port=PORT, unit_id=52)
            # Lakukan operasi pembacaan data
            result = client.read_holding_registers(0, 3)
            if result:
                print("Data yang dibaca dari perangkat Modbus: ", result)
                # Menambahkan penamaan untuk setiap elemen dalam array
                # Mengonversi nilai result[0] dari rentang 0-1023 ke rentang 0-600
                converted_value = math.floor(math.floor(result[0]* 14.5038 * 60 / 1023) * 252/501)
                named_data.update({
                    "Pressure 1" : converted_value
                })
                converted_value = math.floor(math.floor(result[1]* 14.5038 * 60 / 1023) * 175/289)
                named_data.update({
                    "Pressure 2" : converted_value
                })
            else:
                print("Gagal membaca data dari perangkat Modbus.")
                data_json = json.dumps({})  # Data kosong jika gagal
            
            data_json = json.dumps(named_data)
            client.close()
            return jsonify({
                "message": f"Berhasil terhubung ke perangkat Modbus dengan Unit ID 52",
                "data": data_json
            })
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
