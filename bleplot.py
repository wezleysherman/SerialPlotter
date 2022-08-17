import asyncio
from struct import unpack
from bleak import BleakScanner, BleakClient
from multiprocessing import Process, Queue
import socket
import websockets
import os
import json
from datetime import datetime

#addr = "00:80:E1:21:8F:97"
#addr = "00:80:E1:21:93:26"
#addr = "00:80:E1:21:94:B5"
#addr = "80DF2B35-61A8-78B7-169A-4FEECC5FDA6A"
#addr = "27ABEE7C-ACD5-8D15-0E96-E5D1BE9294D8"
addr = "9DD6CBA6-6824-FD78-EF0C-3EE69D0DDA2A"
total_sec = 0
time_calc = 0 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dataQueue = Queue()
last_time = datetime.now()
async def notification_handler(sender, data):
	global sock
	global dataQueue
	global last_time
	global time_calc

	time_now = datetime.now()
	diff = last_time - time_now
	last_time = time_now
	#print("time diff: ", diff.total_seconds())
	#print("Time diff: ", (unpack('<I', data[21:25])[0]-time_calc))
	#print("Calced time diff: ", (unpack('<H', data[25:27])[0]))
	#print("Avg time: ", (unpack('<H', data[31:33])[0]))
	time_calc = unpack('<I', data[21:25])[0]
	if(data[0] == 5):
		idx = 1
		while idx < 101:
			#led_emitting.append(int.from_bytes(data[idx:idx+2], byteorder="little"))#[unpack('<H', data[26:28])[0]]
			print(str(unpack('<f', data[idx:idx+4])[0]))
			#print(str(int.from_bytes(data[idx:idx+4], byteorder="little")))
			#print(str(unpack('<i', data[idx:idx+4])[0]))
			idx += 4
	elif(data[0] == 6):
		print("X ", str(unpack('<f', data[1:5])[0]))
		print("Y ", str(unpack('<f', data[5:9])[0]))
		print("Z ", str(unpack('<f', data[9:13])[0]))
		print("Xi ", str(unpack('<h', data[13:15])[0]))
		print("Yi ", str(unpack('<h', data[15:17])[0]))
		print("Zi ", str(unpack('<h', data[17:19])[0]))
	elif(data[0] == 0):
		print("~~State of Health~~")
		print("Prox status: ", data[1])
		print("Charge Rate: ", data[2])
		print("HR: ", data[3])
		print("Bat Status: ", str(unpack('<f', data[4:8])[0]))
		print("Time: ", str(unpack('<I', data[8:12])[0]))
		print("Time diff: ", (unpack('<I', data[8:12])[0]-time_calc))
		time_calc = unpack('<I', data[8:12])[0]
	elif(data[0] == 2):
		print("--------")
		print("Velocity: ", str(unpack('<f', data[1:5])[0]))
		print("Distance: ", str(unpack('<f', data[5:9])[0]))
		print("TUT: ", str(unpack('<H', data[9:11])[0]))
	elif(data[0] == 0x0F):
		'''
		
		memcpy(&NotifyCharData[13], (unsigned char*)(&rep_set.rep_distance), 4); // Rep Dist
		memcpy(&NotifyCharData[17], (unsigned char*)(&rep_set.rep_idx), 1); // Rep IDX

		memcpy(&NotifyCharData[18], (unsigned char*)(&rep_set.repitions[0].distance), 4); // Rep 0 Dist
		memcpy(&NotifyCharData[22], (unsigned char*)(&rep_set.repitions[0].velocity), 4); // Rep 0 Vel
		memcpy(&NotifyCharData[26], (unsigned char*)(&rep_set.repitions[0].distance), 4); // Rep 0 Dist neg
		memcpy(&NotifyCharData[30], (unsigned char*)(&rep_set.repitions[0].velocity), 4); // Rep 0 Vel neg
		memcpy(&NotifyCharData[34], (unsigned char*)(&rep_set.repitions[0].is_candidate), 1); // Rep 0 is_candidate
		memcpy(&NotifyCharData[35], (unsigned char*)(&rep_set.repitions[0].time_under_tension), 2); // Rep 0 time_under_tension
		memcpy(&NotifyCharData[37], (unsigned char*)(&rep_set.repitions[0].rep_sequence), 1); // Rep 0 rep_seq
		memcpy(&NotifyCharData[38], (unsigned char*)(&rep_set.repitions[0].is_stale), 1); // Rep 0 is_stale

		memcpy(&NotifyCharData[39], (unsigned char*)(&rep_set.repitions[1].distance), 4); // Rep 1 Dist
		memcpy(&NotifyCharData[43], (unsigned char*)(&rep_set.repitions[1].velocity), 4); // Rep 1 Vel
		memcpy(&NotifyCharData[47], (unsigned char*)(&rep_set.repitions[1].distance), 4); // Rep 1 Dist neg
		memcpy(&NotifyCharData[51], (unsigned char*)(&rep_set.repitions[1].velocity), 4); // Rep 1 Vel neg
		memcpy(&NotifyCharData[55], (unsigned char*)(&rep_set.repitions[1].is_candidate), 1); // Rep 1 is_candidate
		memcpy(&NotifyCharData[56], (unsigned char*)(&rep_set.repitions[1].time_under_tension), 2); // Rep 1 time_under_tension
		memcpy(&NotifyCharData[58], (unsigned char*)(&rep_set.repitions[1].rep_sequence), 1); // Rep 1 rep_seq
		memcpy(&NotifyCharData[59], (unsigned char*)(&rep_set.repitions[1].is_stale), 1); // Rep 1 is_stale
		'''
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		print("Accel X: ", str(unpack('<f', data[1:5])[0]))
		print("Int Z Vel: ", str(unpack('<f', data[5:9])[0]))
		print("Int Z Dist: ", str(unpack('<f', data[9:13])[0]))
		print("Rep Dist: ", str(unpack('<f', data[13:17])[0]))
		print("Rep Idx: ", str(data[17]))
		print("---")
		print("Rep 0 Dist pos: ", str(unpack('<f', data[18:22])[0]))
		print("Rep 0 Vel pos: ", str(unpack('<f', data[22:26])[0]))
		print("Rep 0 Dist neg: ", str(unpack('<f', data[26:30])[0]))
		print("Rep 0 Vel neg: ", str(unpack('<f', data[30:34])[0]))
		print("Rep 0 is can: ", str(data[34]))
		print("Rep 0 tut: ", str(unpack('<H', data[35:37])[0]))
		print("Rep 0 seq: ", str(data[37]))
		print("Rep 0 stale: ", str(data[38]))
		print("----")
		print("Rep 1 Dist pos: ", str(unpack('<f', data[39:43])[0]))
		print("Rep 1 Vel pos: ", str(unpack('<f', data[43:47])[0]))
		print("Rep 1 Dist neg: ", str(unpack('<f', data[47:51])[0]))
		print("Rep 1 Vel neg: ", str(unpack('<f', data[51:55])[0]))
		print("Rep 1 is can: ", str(data[55]))
		print("Rep 1 tut: ", str(unpack('<H', data[56:58])[0]))
		print("Rep 1 seq: ", str(data[58]))
		print("Rep 1 stale: ", str(data[59]))
		print("---")
		print("Worst Time: ", str(unpack('<H', data[60:62])[0]))
		print("UP: ", data[62])
		print("DOWN: ", data[63])
		print("UP CT: ", data[64])
		print("UP ST: ", data[65])
		print("DOWN CT: ", data[66])
		print("DOWN ST: ", data[67])

	dataQueue.put(data)
	#sock.sendto(data, ("127.0.0.1", 1969))

async def echo(websocket):
	global dataQueue
	dist = 0
	while(1):
		try:
			await asyncio.sleep(1)
			while not dataQueue.empty():
				data = dataQueue.get()
				if(data[0] == 0x01):
					with open("out.csv", "a") as file:
						file.write(str(unpack('<f', data[5: 9])[0]) + "\n")
					'''
					NotifyCharData[0] = 0x02;
					memcpy(&NotifyCharData[1], (unsigned char*)(&acc_buff[0]), 4);
					memcpy(&NotifyCharData[5], (unsigned char*)(&acc_buff[1]), 4);
					memcpy(&NotifyCharData[9], (unsigned char*)(&acc_buff[2]), 4);
					memcpy(&NotifyCharData[13], (unsigned char*)(&velocity), 4);
					memcpy(&NotifyCharData[17], (unsigned char*)(&calcVelocity), 4);
					'''
					curr_dist = unpack('<f', data[27:31])[0]
					if(curr_dist != dist):
						dist = curr_dist
					#print("Dist: ", dist)
					acc = [unpack('<f', data[9:13])[0], unpack('<f', data[5:9])[0], 0]#unpack('<f', data[9: 13])[0]]
					#gyro = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
					#quat = [unpack('<f', data[26:30])[0], unpack('<f', data[30: 34])[0], unpack('<f', data[34: 38])[0], unpack('<f', data[38: 42])[0]]
					pyr = [0, 0, 0]#[unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
					velocity = data[62]#unpack('<f', data[5:9])[0]
					calcVelocity = data[63]#unpack('<f', data[9:13])[0]

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
				elif(data[0] == 0x02):
					#print("Dist: ", dist)
					acc = [unpack('<f', data[1:5])[0], unpack('<f', data[5:9])[0], 0]#unpack('<f', data[9: 13])[0]]
					#gyro = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
					#quat = [unpack('<f', data[26:30])[0], unpack('<f', data[30: 34])[0], unpack('<f', data[34: 38])[0], unpack('<f', data[38: 42])[0]]
					pyr = [0, 0, 0]#[unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
					velocity = 0#data[62]#unpack('<f', data[5:9])[0]
					calcVelocity = 0#data[63]#unpack('<f', data[9:13])[0]

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

					
					acc = [0, 0, 0]
					#gyro = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
					#quat = [unpack('<f', data[26:30])[0], unpack('<f', data[30: 34])[0], unpack('<f', data[34: 38])[0], unpack('<f', data[38: 42])[0]]
					pyr = [0, 0, 0]
					velocity = 0
					calcVelocity = 0
					led_emitting = []
					idx = 1
					while idx < 101:
						#led_emitting.append(int.from_bytes(data[idx:idx+2], byteorder="little"))#[unpack('<H', data[26:28])[0]]
						led_emitting.append(unpack('<f', data[idx:idx+4])[0])#[unpack('<H', data[26:28])[0]]
						idx += 4
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
						))
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
				#await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0200"))

				await asyncio.sleep(2)
				await client.start_notify("0000fe42-8e22-4541-9d4c-21edae82ed19", notification_handler)
				await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0100"))
				await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0A0B"))

				#await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0300"))
				
				
				while(1):
					await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0B00"))
					await asyncio.sleep(10)
					await client.write_gatt_char("0000fe41-8e22-4541-9d4c-21edae82ed19", bytes.fromhex("0C00"))
					await asyncio.sleep(3)
				
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
 