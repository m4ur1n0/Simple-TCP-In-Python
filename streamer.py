# do not import anything else from loss_socket besides LossyUDP
import random
import struct
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY


class Streamer:
    def __init__(self, dst_ip, dst_port,
                 src_ip=INADDR_ANY, src_port=0):
        """Default values listen on all network interfaces, chooses a random source port,
           and does not introduce any simulated packet loss."""
        self.src_port = src_port
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        # MY member vars
        # length of the header (in bytes)
        self.size_of_header = 12
        self.header_format_string = "2h2I"
        # start with a random sequence number, we'll wrap back around if that needs to change
        # self.sequence = random.randint(0, 4294967295)
        self.sequence = 0
        # as of right now acknum is worthless, and implementation will have to be changed, but we want size to work
        # self.acknum = random.randint(0, 4294967295)
        self.acknum = 1
        self.recv_buff = {}

    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        # break into blocks of 1472 bytes each, and send those as you go 
        # but before adding sending anything, append a header to the front
        # of each block 
        block = b""
        


        while len(data_bytes) >= 1472 - self.size_of_header:
            # create a header (2 shorts, 2 ints) to communicate
            # source port, dst port, seq # and (we'll add ack # later?)
            # sequence number is sent as 1 more than the current saved
            # seq and then seq is updated after sending
            header = struct.pack(self.header_format_string, self.src_port, self.dst_port, self.sequence + 1, self.acknum + 1)

            # set up block
            block = data_bytes[0:1472 - self.size_of_header]
            data_bytes = data_bytes[1472 - self.size_of_header:]

            # increment header fields
            bsize = len(block)
            if (self.sequence + bsize <= 4294967295):
                self.sequence += bsize
            else:
                # there may be a shifty 1 that needs dealing with here
                diff = 4294967295 - self.sequence
                self.sequence = bsize - diff
            
            self.acknum = self.acknum # this will get changed after PART 2

            self.socket.sendto(header + block, (self.dst_ip, self.dst_port))

        # final or small packet -- have to redo basically everything from the loop out here
        # if there's still more to send 
        block = data_bytes
        if block:
            header = struct.pack(self.header_format_string, self.src_port, self.dst_port, self.sequence + 1, self.acknum + 1)
            bsize = len(block)
            if (self.sequence + bsize <= 4294967295):
                self.sequence += bsize
            else:
                # there may be a shifty 1 that needs dealing with here
                diff = 4294967295 - self.sequence
                self.sequence = bsize - diff

            self.acknum = self.acknum # this will get changed after PART 2

            self.socket.sendto(header + block, (self.dst_ip, self.dst_port))

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""


        # ack holds the value of the seq num we're expecting
        # and AFTER receiving a packet and exiting the loop,
        # it holds the value of the ack to send
        #ack = 1

        while True:

            # check if the current expected pkt is in the buffer rn
            try:
                # pops it so as to remove from the buffer
                # get to call it dfield immediately bc things
                # are only added to the buffer as data field 
                dfield = self.recv_buff.pop(self.acknum)

                # need to update the acknum
                bsize = len(dfield)
                if (self.acknum + bsize <= 4294967295):
                    self.acknum += bsize
                else:
                    # there may be a shifty 1 that needs dealing with here
                    diff = 4294967295 - self.acknum
                    self.acknum = bsize - diff
                
                return dfield  
            except:
                pass

            data, addr = self.socket.recvfrom()
            datafield = data[self.size_of_header:]

            # get all of the packed vars in the header from the first header_size bytes of the data
            srcP, dstP, seqN, ackN = struct.unpack(self.header_format_string, data[0:self.size_of_header])
            # print('rcvd pkt %d   :   expecting pkt %d' %(seqN, self.acknum))


            # if not our expected seq num, store it in the buffer
            # if it is our expected seq num, for PART 2, just quit
            # and return the data from that on its own 
            if (seqN != self.acknum):
                self.recv_buff[seqN] = datafield
                
            else:
                # retDat += datafield
                bsize = len(datafield)
                if (self.acknum + bsize <= 4294967295):
                    self.acknum += bsize
                else:
                    # there may be a shifty 1 that needs dealing with here
                    diff = 4294967295 - self.acknum
                    self.acknum = bsize - diff

                return datafield
        

        

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        pass
