import pickle
import socket
import struct
import time


def sanitize_key(key):
    if key is None:
        return key
    replacements = {
        ".": "_",
        " ": "_",
    }
    for old, new in replacements.items():
        key = key.replace(old, new)
    return key


class Graphite:
    def __init__(self, host="fifemondata.fnal.gov", pickle_port=2004, logger=None):
        self.graphite_host = host
        self.graphite_pickle_port = pickle_port
        self.logger = logger

    def send_dict(self, namespace, data, debug_print=True, send_data=True):
        """send data contained in dictionary as {k: v} to graphite dataset
        $namespace.k with current timestamp"""
        if data is None and self.logger is not None:
            self.logger.warning("Warning: send_dict called with no data")
            return
        now = int(time.time())
        post_data = []
        # turning data dict into [('$path.$key',($timestamp,$value)),...]]
        for k, v in data.items():
            t = (namespace + "." + k, (now, v))
            post_data.append(t)
            if debug_print and self.logger is not None:
                self.logger.debug(f"{t}")
        # pickle data
        payload = pickle.dumps(post_data, protocol=2)
        header = struct.pack("!L", len(payload))
        message = header + payload

        if not send_data:
            return
        # throw data at graphite

        s = socket.socket()
        try:
            s.connect((self.graphite_host, self.graphite_pickle_port))
            s.sendall(message)
        except OSError:
            if self.logger is not None:
                self.logger.exception(
                    f"Error sending data to graphite at {self.graphite_host}:{self.graphite_pickle_port}"
                )
        finally:
            s.close()


if __name__ == "__main__":
    data = {"count1": 5, "count2": 0.5}
    g = Graphite()
    g.send_dict("test", data, send_data=False)
