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
        result = client.read_holding_registers(0, 7)
        if result:
            print("Data yang dibaca dari perangkat Modbus:", result)
            # Menambahkan penamaan untuk setiap elemen dalam array
            named_data = {
                f"Data {i+1}": result[i] for i in range(len(result))
            }
            # Mengubah data menjadi format JSON
            data_json = json.dumps(named_data)
        else:
            print("Gagal membaca data dari perangkat Modbus.")
            data_json = json.dumps({})  # Data kosong jika gagal

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
