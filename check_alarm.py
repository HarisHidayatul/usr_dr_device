import csv
import requests
# Import library untuk Modbus
from pyModbusTCP.client import ModbusClient

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
def read_csv_to_2d_array(file_path):
    try:
        with open(file_path, 'r') as csv_file:
            # Membaca file CSV
            csv_reader = csv.reader(csv_file)

            # Mengonversi setiap baris CSV menjadi array dan menampungnya dalam list
            csv_data = [row for row in csv_reader]

            return csv_data
    except FileNotFoundError:
        return [[f"File '{file_path}' tidak ditemukan."]]
    except Exception as e:
        return [[f"Terjadi kesalahan: {e}"]]

def overwrite_csv(file_path, target_row_index, target_column_index, new_value):
    csv_data = read_csv_to_2d_array(file_path)

    if len(csv_data) > target_row_index and len(csv_data[0]) > target_column_index:
        csv_data[target_row_index][target_column_index] = new_value

        try:
            with open(file_path, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerows(csv_data)

            print(f"Data berhasil di-overwrite pada baris {target_row_index} dan kolom {target_column_index}.")
        except Exception as e:
            print(f"Terjadi kesalahan saat menulis kembali ke file CSV: {e}")
    else:
        print(f"Indeks baris {target_row_index} atau kolom {target_column_index} diluar batas.")

def loop_chiller_board(file_path):
    # Ganti 'nama_file.csv' dengan nama file CSV yang ingin Anda baca
    file_path = 'chiller_board.csv'

    csv_2d_array = read_csv_to_2d_array(file_path)
    message_all = []
    if(len(csv_2d_array) > 1):
        panjang_data = len(csv_2d_array[0])-1
        # print(panjang_data)
        for i in range(panjang_data):
            IP = csv_2d_array[1][i+1]
            Address = csv_2d_array[2][i+1]
            message_chiller = []
            inlet_temperature = 0
            outlet_temperature = 0
            #Lakukan baca data pada area input register
            client = ModbusClient(host=IP, port=502, unit_id=int(Address),timeout=1)
            
            if client.open():
                result = client.read_input_registers(2000, 8)
                # print(csv_2d_array[0][i+1])
                if result:
                    # print(csv_2d_array[0][i+1])
                    unit_fault = int(result[0])
                    system1_fault = int(result[1])
                    system2_fault = int(result[2])
                    system_12fault = int(result[6])
                
                    unit_fault_csv = int(csv_2d_array[4][i+1])
                    system1_fault_csv = int(csv_2d_array[5][i+1])
                    system2_fault_csv = int(csv_2d_array[6][i+1])
                    system_12fault_csv = int(csv_2d_array[7][i+1])
                
                    inlet_temperature = int(result[4])
                    outlet_temperature = int(result[5])
                    ambient_air_temperature = int(result[3])
                
                    overwrite_csv(file_path,13,i+1,inlet_temperature)
                    overwrite_csv(file_path,14,i+1,outlet_temperature)
                    overwrite_csv(file_path,12,i+1,ambient_air_temperature)
                
                
                    if(unit_fault != unit_fault_csv):
                        overwrite_csv(file_path,4,i+1,unit_fault)
                        array_all_error = display_error_messages(decimal_to_16_bit_array(unit_fault),0)
                        temp_list_error = []
                        for list_error in array_all_error:
                            if list_error:
                                temp_list_error.append(list_error)
                        if len(temp_list_error) > 0:
                            message_chiller.append('Error : Terjadi Error Pada Unit Fault')
                            for loop_error in temp_list_error:
                                message_chiller.append(loop_error)
                            message_chiller.append('')
                        # print('error, unit fault')
                    if(system1_fault != system1_fault_csv):
                        overwrite_csv(file_path,5,i+1,system1_fault)
                        array_all_error = display_error_messages(decimal_to_16_bit_array(system1_fault),1)
                        temp_list_error = []
                        for list_error in array_all_error:
                            if list_error:
                                temp_list_error.append(list_error)
                        if len(temp_list_error) > 0:
                            message_chiller.append('Error : Terjadi Error Pada System 1 Fault')
                            for loop_error in temp_list_error:
                                message_chiller.append(loop_error)
                            message_chiller.append('')
                        # print('error, system 1 fault')
                    if(system2_fault != system2_fault_csv):
                        overwrite_csv(file_path,6,i+1,system2_fault)
                        array_all_error = display_error_messages(decimal_to_16_bit_array(system2_fault),2)
                        temp_list_error = []
                        for list_error in array_all_error:
                            if list_error:
                                temp_list_error.append(list_error)
                        if len(temp_list_error) > 0:
                            message_chiller.append('Error : Terjadi Error Pada System 2 Fault')
                            for loop_error in temp_list_error:
                                message_chiller.append(loop_error)
                            message_chiller.append('')
                        # print('error, system 2 fault')
                    if(system_12fault != system_12fault_csv):
                        overwrite_csv(file_path,7,i+1,system_12fault)
                        array_all_error = display_error_messages(decimal_to_16_bit_array(system_12fault),3)
                        temp_list_error = []
                        for list_error in array_all_error:
                            if list_error:
                                temp_list_error.append(list_error)
                        if len(temp_list_error) > 0:
                            message_chiller.append('Error : Terjadi Error Pada System 1 2 Fault')
                            for loop_error in temp_list_error:
                                message_chiller.append(loop_error)
                            message_chiller.append('')
                        # print('error, system 1 2 fault')
            
                #Lakukan baca data untuk mendapatkan data setting water outlet
                result = client.read_input_registers(5005, 1)
                if result:
                    water_outlet_set_in_cooling = result[0]
                    overwrite_csv(file_path,11,i+1,water_outlet_set_in_cooling)
            
                #Lakukan baca data untuk mendapatkan data compressor ratio
                result = client.read_input_registers(5010, 1)
                if result:
                    compressor_output_ratio = result[0]
                    overwrite_csv(file_path,9,i+1,compressor_output_ratio)
            
                #Lakukan baca data pada area holding register untuk mengecek mesin ON/OFF
                result = client.read_holding_registers(0, 5)
                if result:
                    on_off_status = int(result[0])
                    set_temp_chiller = int(result[2])
                    set_temp_chiller_in_heating = int(result[3])
                
                    on_off_status_csv = int(csv_2d_array[3][i+1])
                    set_temp_chiller_csv = int(csv_2d_array[8][i+1])
                
                    overwrite_csv(file_path,8,i+1,set_temp_chiller)
                    overwrite_csv(file_path,10,i+1,set_temp_chiller_in_heating)
                
                    if(on_off_status != on_off_status_csv):
                        overwrite_csv(file_path,3,i+1,on_off_status)
                        # print('System on/off')
                        if(on_off_status == 1):
                            set_temp_chiller_float = set_temp_chiller/10
                            message_chiller.append('Chiller ON')
                            message_chiller.append(f'Settingan Suhu Pada Mesin : {set_temp_chiller_float}')
                        if(on_off_status == 0):
                            message_chiller.append('Chiller OFF')
                        inlet_temperature_float = inlet_temperature/10
                        outlet_temperature_float = outlet_temperature/10
                        message_chiller.append(f'Suhu inlet : {inlet_temperature_float}')
                        message_chiller.append(f'Suhu outlet : {outlet_temperature_float}')
                        message_chiller.append('')
                    
                    if(on_off_status == 1):
                        if(set_temp_chiller != set_temp_chiller_csv):
                            set_temp_chiller_float = set_temp_chiller/10
                            set_temp_chiller_csv_float = set_temp_chiller_csv/10
                            message_chiller.append(f'Terjadi perubahan suhu setting chiller dari {set_temp_chiller_csv_float} menjadi {set_temp_chiller_float}')
                            message_chiller.append('')
                
                    if len(message_chiller) > 0:
                        message_all.append(f'*Chiller : {csv_2d_array[0][i+1]}*')
                        for loop_message in message_chiller:
                            message_all.append(loop_message)
                client.close()
            else:
                # overwrite_csv(file_path,13,i+1,inlet_temperature)
    
    message_text = ''
    # print(message_all)
    for loop_message in message_all:
        message_text = message_text + loop_message
        message_text = message_text + '\n'
    
    base_url = "http://192.168.1.231/karutimbang/auto_alarm_wa.php"
    # Membuat URL lengkap dengan parameter
    full_url = f"{base_url}?alm={message_text}"

    if len(message_all) > 0:
        response = requests.get(full_url)
        if response.status_code == 200:
            print(f"GET request berhasil! Hasil: {response.text}")
        else:
            print(f"GET request gagal! Status code: {response.status_code}")
    
                        
if __name__ == "__main__":
    while True:
        file_path = 'chiller_board.csv'
        loop_chiller_board(file_path)
        csv_2d_array = read_csv_to_2d_array(file_path)    
        # Menampilkan data dengan menggunakan loop dan index
        for i in range(len(csv_2d_array)):
            print(f"Baris {i + 1}: {csv_2d_array[i]}")