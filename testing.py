import fins.udp
import time

class finsUdpOmron:
    def __init__(self, IP, dest_node_add, src_node_address):
        self.IP = IP
        self.dest_node_add = dest_node_add
        self.srce_node_add = src_node_address

    @staticmethod
    def convert_to_fins_format(number):
        # Konversi angka ke format byte string FINS
        low_byte = number & 0xFF
        high_byte = (number >> 8) & 0xFF
        return bytes([0x00, low_byte, 0x00, high_byte])

    def read_data_memory(self, address):
        # # Buat objek koneksi FINS
        # fins_instance = fins.udp.UDPFinsConnection()
        # # Lakukan koneksi ke PLC
        # fins_instance.connect(self.IP)
        # fins_instance.dest_node_add = self.dest_node_add
        # fins_instance.srce_node_add = self.srce_node_add
        print(self.convert_to_fins_format(address))

        # try:
        #     # Baca data dari alamat memory
        #     mem_area = fins_instance.memory_area_read(fins.FinsPLCMemoryAreas().DATA_MEMORY_WORD, self.convert_to_fins_format(address))
        #     print(f'Nilai dari D{address} = {mem_area}')
        # except Exception as e:
        #     print(f"Error: {e}")

if __name__ == "__main__":
    # finsOmron = finsUdpOmron(IP='192.168.2.103', dest_node_add=1, src_node_address=25)
    # finsOmron.read_data_memory(address=100)
    print(b'\x00\x64\x00')
    print(finsUdpOmron.convert_to_fins_format(100))

