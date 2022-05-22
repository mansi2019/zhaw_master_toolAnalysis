from deeptone import Deeptone
from scipy.io import wavfile
import json

def input_generator(filepath, chunk_size=512):
    print(f"Opening file {filepath}")
    rate, data = wavfile.read(filepath)
    print(f"Detected sample rate: {rate}")

    index = 0
    while index < len(data):
        yield data[index: min(len(data), index + chunk_size)]
        index += chunk_size
    return

# Initialise Deeptone
engine = Deeptone(license_key="YTQ5OTZmNzEyODM5NGViMjgzOTIxYTgxY2E3Mjc1M2Z8aFppLWNhVzFncWR0V1I4YkNRN29jUWxRNGJGQjRzTWNOYVJXQW1HSmk4cz0")
audio_generator = input_generator("/home/singhma3/masterarbeit/wav/03a01Fa.wav")

output = engine.process_stream(
    input_generator=audio_generator,
    models=[engine.models.Gender, engine.models.Emotions],
    output_period=512,
    volume_threshold=0.005,
    include_raw_values=True
)

for ts_result in output:
    print(json.dumps(ts_result, indent=4, sort_keys=True))