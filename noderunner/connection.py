"""Module containing classes and functions related to connctions"""
import six
import struct
import json

# A message comprises of two parts
# the Header which is 8 bits long consists of:
# * An unsigned byte with the protocol version
# * An unsigned byte with the message type
# * Two unused bytes
# * An unsigned 32-bit integer containing length of message
header = struct.Struct("!BBxxI")
# the Body, a UTF-8 encoded JSON string


class Connection(object):
    _supported_versions = (1,)
    _version = 1

    def __init__(self, socket):
        self._socket = socket
        self._run = True


    def _read_header(self):
        version, mtype, n = header.unpack(self._socket.read(header.size))
        if not version in self._supported_versions:
            raise RuntimeError("Unsupported protocol version {0}"
                               .format(version))

        return mtype, n

    def _read_body(self, n):
        return json.loads(self._socket.read(n))

    def read_packet(self):
        method, n = self._read_header()
        return method, self._read_body(n)

    def send_packet(self, kind, body):
        enc = bytes(six.u(json.dumps(body)).encode("utf8"))
        n = len(enc)
        hdr = header.pack(self._version, kind, n)
        self._socket.write(hdr + enc)

    def packets(self):
        while self._run and not self._socket.closed:
            yield self.read_packet()
