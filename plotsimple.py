import asyncio
from struct import unpack
from bleak import BleakScanner, BleakClient
from multiprocessing import Process, Queue
import socket
import websockets
import json

#addr = "00:80:E1:21:8F:97"
addr = "00:80:E1:21:93:26"

total_rec = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dataQueue = Queue()

async def notification_handler(sender, data):
	global sock
	global dataQueue
	if(data[0] == 1):
		#acc = [unpack('<f', data[2:6])[0], unpack('<f', data[6: 10])[0], unpack('<f', data[10: 14])[0]]
		#gyro = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
		#quat = [unpack('<f', data[26:30])[0], unpack('<f', data[30: 34])[0], unpack('<f', data[34: 38])[0], unpack('<f', data[38: 42])[0]]
		pyr = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
		led_emitting = 0#[unpack('<H', data[26:28])[0]]
		#print(led_emitting)
		print("Vel Z: ", unpack('<f', data[2:6])[0])
	#else:
	#	print("Batt life: ", unpack('<f', data[2:6])[0])
	#sock.sendto(data, ("127.0.0.1", 1969))


async def bluetooth_async():
	devices = await BleakScanner.discover()
	for d in devices:
		print(d)
	while(1):
		#await asyncio.sleep(1)
		try:
			async with BleakClient(addr) as client:
				print(f"Connected: {client.is_connected}")
				svcs = await client.get_services()
				print("Services:")

				for service in svcs:
					print(service)
				#await client.stop_notify("0000fe42-8e22-4541-9d4c-21edae82ed19")
				#await client.start_notify("0000fe42-8e22-4541-9d4c-21edae82ed19", notification_handler)
				#await client.stop_notify("0000fe42-8e22-4541-9d4c-21edae82ed19")
				#await client.stop_notify("0000FE23-8e22-4541-9d4c-21edae82ed19")
				await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0100"))
				await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0200"))
				await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0300"))

				await asyncio.sleep(2)
				await client.start_notify("0000fe42-8e22-4541-9d4c-21edae82ed19", notification_handler)

				print("Notify Started")
				await asyncio.Future()  # run forever
				await client.stop_notify("0000fe42-8e22-4541-9d4c-21edae82ed19")
		except Exception as e:
			print(e)
			print("err retrying")
			continue




async def main():
	f1 = loop.create_task(bluetooth_async())
	await asyncio.Future()  # run forever
	
	

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
 