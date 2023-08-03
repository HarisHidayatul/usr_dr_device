from flask import Flask, jsonify
import json

# Import library untuk Modbus
from pyModbusTCP.client import ModbusClient

app = Flask(__name__)

# Definisikan host dan port sebagai variabel global
HOST = '192.168.1.229'
PORT = 502

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
            
        result = client.read_input_registers(5002, 1)
        if result:
            print("Data yang dibaca dari perangkat Modbus:", result)
            # Menambahkan penamaan untuk setiap elemen dalam array
            
            named_data.update({
                "Water inlet temperature setting in cooling mode": result[0],
            })
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal
        
        
        result = client.read_input_registers(5006, 1)
        if result:
            named_data.update({
                "Water outlet temperature setting in cooling mode": result[0]
            })
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal
        
        result = client.read_input_registers(5011, 1)
        if result:
            named_data.update({
                "Compressor output ratio": result[0]
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
def read_input_register_1(unit_id):
    try:
        client = ModbusClient(host=HOST, port=PORT, unit_id=unit_id)
        
        # Lakukan operasi pembacaan data
        # client.write_single_register(2,120)
        result = client.read_holding_registers(0, 8)
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
            
        result = client.read_input_registers(5002, 1)
        if result:
            print("Data yang dibaca dari perangkat Modbus:", result)
            # Menambahkan penamaan untuk setiap elemen dalam array
            
            named_data.update({
                "Water inlet temperature setting in cooling mode": result[0],
            })
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal
        
        
        result = client.read_input_registers(5006, 1)
        if result:
            named_data.update({
                "Water outlet temperature setting in cooling mode": result[0]
            })
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal
        
        result = client.read_input_registers(5011, 1)
        if result:
            named_data.update({
                "Compressor output ratio": result[0]
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
        
if __name__ == '__main__':
    app.run(debug=True)
