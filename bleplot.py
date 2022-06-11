import asyncio
from struct import unpack
from bleak import BleakScanner, BleakClient
from multiprocessing import Process, Queue
import socket
import websockets
import json

#addr = "00:80:E1:21:8F:97"
#addr = "00:80:E1:21:93:26"
addr = "00:80:E1:21:94:B5"

total_rec = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dataQueue = Queue()

async def notification_handler(sender, data):
	global sock
	global dataQueue
	idx = 1
	while idx < 101:
		#led_emitting.append(int.from_bytes(data[idx:idx+2], byteorder="little"))#[unpack('<H', data[26:28])[0]]
		print(str(unpack('<f', data[idx:idx+4])[0]))
		idx += 4
	dataQueue.put(data)
	#sock.sendto(data, ("127.0.0.1", 1969))

async def echo(websocket):
	global dataQueue

	while(1):
		try:
			await asyncio.sleep(1)
			while not dataQueue.empty():
				data = dataQueue.get()
				if(data[0] == 2):
					acc = [unpack('<f', data[2:6])[0], unpack('<f', data[6: 10])[0], unpack('<f', data[10: 14])[0]]
					#gyro = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
					#quat = [unpack('<f', data[26:30])[0], unpack('<f', data[30: 34])[0], unpack('<f', data[34: 38])[0], unpack('<f', data[38: 42])[0]]
					pyr = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
					velocity = unpack('<f', data[26:30])[0]
					calcVelocity = unpack('<f', data[30:34])[0]

					led_emitting = [0]#[unpack('<H', data[26:28])[0]]
					#print("Reps: ", int.from_bytes(data[18:22], byteorder="little"))
					#print("Velcoity: ", unpack('<f', data[22:26])[0])
					#print(led_emitting)
					await websocket.send(
						json.dumps({
							"accel": acc,
							"euler": pyr,
							"velocity": velocity,
							"calcVelocity": calcVelocity,
							"led": led_emitting
							}
						))
				elif(data[0] == 5):

					'''
					acc = [0, 0, 0]
					#gyro = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
					#quat = [unpack('<f', data[26:30])[0], unpack('<f', data[30: 34])[0], unpack('<f', data[34: 38])[0], unpack('<f', data[38: 42])[0]]
					pyr = [0, 0, 0]
					velocity = 0
					calcVelocity = 0
					led_emitting = []
					idx = 1
					while idx < 21:
						led_emitting.append(int.from_bytes(data[idx:idx+2], byteorder="little"))#[unpack('<H', data[26:28])[0]]
						idx += 2
					#print("Reps: ", int.from_bytes(data[18:22], byteorder="little"))
					#print("Velcoity: ", unpack('<f', data[22:26])[0])
					print(led_emitting)
					await websocket.send(
						json.dumps({
							"accel": acc,
							"euler": pyr,
							"velocity": velocity,
							"calcVelocity": calcVelocity,
							"led": led_emitting
							}
						))'''
				#else:
				#	print("Batt life: ", unpack('<f', data[2:6])[0])
		except Exception as e:
			print(e)
			continue

async def bluetooth_async():
	global dataQueue

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
				#await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0200"))

				await asyncio.sleep(2)
				await client.start_notify("0000fe42-8e22-4541-9d4c-21edae82ed19", notification_handler)
				await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0300"))
				await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0A0F"))
				#await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0900"))

				#await asyncio.sleep(20)
				#await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0500"))

				print("Notify Started")
				
				await asyncio.Future()  # run forever
				await client.stop_notify("0000fe42-8e22-4541-9d4c-21edae82ed19")
		except Exception as e:
			print(e)
			print("err retrying")
			continue


async def webserver_async():
	async with websockets.serve(echo, "127.0.0.1", 1968):
		await asyncio.Future()  # run forever

async def main():
	f1 = loop.create_task(bluetooth_async())
	f2 = loop.create_task(webserver_async())
	await asyncio.Future()  # run forever
	
	

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
 