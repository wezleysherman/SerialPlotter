import asyncio
from struct import unpack
from bleak import BleakScanner, BleakClient
from multiprocessing import Process, Queue
import socket

firmware = open("Firmware.bin", "rb")
firmware_arr = bytearray()

byte = firmware.read(1)
while(byte):
	firmware_arr.append(byte[0])
	byte = firmware.read(1)

firmware.close()



#addr = "00:80:E1:21:8F:97"
#addr = "00:80:E1:21:8F:98"

#addr = "00:80:E1:21:93:27"
#addr = "00:80:E1:21:93:26"

addr = "00:80:E1:21:94:B6"

total_rec = 0
firmware_len = len(firmware_arr)
idx = 0
client = None

async def notification_handler(sender, data):
	print("Rec: ", data)
	global idx
	global client
	await asyncio.sleep(0.1)

	
async def main():
	devices = await BleakScanner.discover()
	for d in devices:
		print(d)
	global client
	global idx

	while(1):
		try:
			async with BleakClient(addr) as client:

				for service in client.services:
					print("s", service)
					for char in service.characteristics:
						print("c",char)
				if addr == "00:80:E1:21:93:26" or addr == "00:80:E1:21:8F:97" or addr == "00:80:E1:21:94:B5":	
					print("found")
					await client.write_gatt_char("0000fe43-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("010FFF"))
					print("sent command")

				elif addr == "00:80:E1:21:93:27" or addr == "00:80:E1:21:8F:98" or addr == "00:80:E1:21:94:B6":	
					print(f"Connected: {client.is_connected}")
					svcs = await client.get_services()
					print("Services:")

					for service in svcs:
						print(service)
					
					print("Starting notify")
					#await client.stop_notify("0000fe23-8e22-4541-9d4c-21edae82ed19")
					await client.start_notify("0000fe23-8e22-4541-9d4c-21edae82ed19", notification_handler)
					await asyncio.sleep(3)
					print("Writing firmware length: ", firmware_len)
					await client.write_gatt_char("0000fe22-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("02007000"))
					await asyncio.sleep(3)
					while(idx < firmware_len):
						await asyncio.sleep(0.1)
						end_idx = idx+100
						if(end_idx > firmware_len):
							end_idx = firmware_len
						await client.write_gatt_char("0000fe24-8e22-4541-9d4c-21edae82ed19", firmware_arr[idx: end_idx])
						print("writing firmware idx: ", idx)
						idx += 100

						if(end_idx == firmware_len):
							print("Writing finish flag")
							#await client.stop_notify("0000FE23-8e22-4541-9d4c-21edae82ed19")
							await asyncio.sleep(3)
							await client.write_gatt_char("0000fe22-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("07007000"))

					await asyncio.sleep(980.0)
					await client.stop_notify("0000FE23-8e22-4541-9d4c-21edae82ed19")
		except Exception as e:
			print("E: ", e)
			continue

asyncio.run(main())
