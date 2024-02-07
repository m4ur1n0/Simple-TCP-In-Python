import struct
header = struct.pack("2h2i", 0, 4466, 4589205, 215563)

# print(header)
# print("\n\n", len(header), "\n\n")
# for i, b in enumerate(header):
#     print(header[i:i+1].hex())


# a, b, c, d = struct.unpack("2h2i", header)

# print("\n\n", a, b, c, d, "\n\n")


budd = {1 : 'bytes', 2 : b'bytes', 3 : 'fuck'}
print (2 in budd.keys())

print(budd[2])