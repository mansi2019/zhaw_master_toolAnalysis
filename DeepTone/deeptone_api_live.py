import time
import threading

# dependencies
import pyaudio
import websocket

# REPLACE WITH YOUR KEY
API_KEY = "ZjFhZTRhYWQ0ZDAzNDE2ODk4NGM0ODY4N2ZmNDM1MDN8RlVNVmxMWEkwa1VKdmNxX3ptNEIzaXdHbkY2VVZwdkdzaWJSdHF1WVhvMD0"

# Send a message to the API every second. Lower this number if you want a lower latency
CHUNK_SIZE = 1024

# Define microphone input stream
pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=CHUNK_SIZE,
)


# What to do with results
def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


# Once websocket connection is established start sending microphone input stream
def on_open(ws):
    stream.start_stream()

    def run():
        while stream.is_active():
            data = stream.read(CHUNK_SIZE)
            ws.send(bytearray(data), websocket.ABNF.OPCODE_BINARY)
        ws.close()

    thread = threading.Thread(target=run)
    thread.start()


if __name__ == "__main__":
    ws = websocket.WebSocketApp(f"wss://api.oto.ai/stream?models=speech&output_period={CHUNK_SIZE}&volume_threshold=0.0",
                                header={'X-API-KEY': API_KEY},
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()