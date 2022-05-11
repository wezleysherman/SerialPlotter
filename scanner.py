import asyncio
from struct import unpack
from bleak import BleakScanner, BleakClient
from multiprocessing import Process, Queue
import socket

addr = "00:80:E1:21:8F:97"
#addr = "00:80:E1:21:93:26"
total_rec = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def notification_handler(sender, data):
	global sock
	print("N")
	sock.sendto(data, ("127.0.0.1", 1969))

async def main():
	while(1):
		devices = await BleakScanner.discover()
		for d in devices:
			print(d)

asyncio.run(main())
 