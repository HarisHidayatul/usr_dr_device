from pyModbusTCP.client import ModbusClient
try:
   c = ModbusClient(host='192.168.1.229', port=502, unit_id=2, debug=True)
   print('Berhasil')
   c.write_multiple_registers(2000, 5)
except ValueError:
   print("Error with host or port params")