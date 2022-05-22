from fileinput import filename
import http.client
import time
import json


import pandas as pd
import os
from pydub import AudioSegment



API_KEY = "ZjFhZTRhYWQ0ZDAzNDE2ODk4NGM0ODY4N2ZmNDM1MDN8RlVNVmxMWEkwa1VKdmNxX3ptNEIzaXdHbkY2VVZwdkdzaWJSdHF1WVhvMD0"
conn = http.client.HTTPSConnection("api.oto.ai")

def main():

    results = []
    results.append(["filename", "happy_percentage", "tired_percentage","neutral_percentage", "silence_percentage", "irritated_percentage", "no_speech_percentage"])

    directory = os.fsencode('/home/singhma3/masterarbeit/wav/')

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".wav"):
            filepath = directory+file
            result = get_emotions(filepath, file)
            results.append(result)
        else:
            print("Skip" + file)   
    
    df = pd.DataFrame(results)
    df.to_csv('deeptone_results_.csv',index=False)


    # ============== Test with two merged files ==============

#    file1 = '/home/singhma3/masterarbeit/wav/16a01Fc.wav'
#    file2 = '/home/singhma3/masterarbeit/wav/16a05Fc.wav'

#    filename1 = os.path.basename(file1).replace(".wav","")
#    filename2 = os.path.basename(file2).replace(".wav","")

#    sound1 = AudioSegment.from_wav(file1)
#    sound2 = AudioSegment.from_wav(file2)

#    combined_sounds = sound1 + sound2
#    file_merged = "/home/singhma3/masterarbeit/wav_test/merged/"+filename1+"_"+filename2+".wav"
#    combined_sounds.export(file_merged, format="wav")
#
#    print("file1")
#    get_emotions(file1, os.fsdecode(file1))
#    print("file2")
#    get_emotions(file2, os.fsdecode(file2))
#    print("merged")
#    get_emotions(file_merged, os.fsdecode(file_merged))

def get_emotions(local_audio_file, file):
    
    all_results = []

    # ============== Processing request using a url to a file ==============

    # REPLACE with your URL
    # payload = '{"url":"https://my-bucket.s3.amazonaws.com/audio.wav"}'

    # post_headers = {
    #     'content-type': "application/json",
    #     'x-api-key': API_KEY
    #     }
    # conn.request("POST", "/file-processing/jobs?models=gender&output_period=4096&include_summary=true&include_transitions=true&include_raw_values=true&volume_threshold=0.001", payload, post_headers)
    # ===============================================================

    # ======= Processing request using direct file upload ===========
    
    with open(local_audio_file, 'rb') as f:
        data = f.read()

    post_headers = {
        'content-type': "audio/wav",
        'x-api-key': API_KEY
        }

    #conn.request("POST", "/file-processing/jobs?models=emotions&output_period=4096&include_summary=true&include_transitions=true&include_raw_values=true&volume_threshold=0.001", data, post_headers)
    conn.request("POST", "/file-processing/jobs?models=emotions&output_period=4096&include_summary=true&include_transitions=true&include_raw_values=true&volume_threshold=0.001", data, post_headers)
    # ================================================================

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))

    job_id = json.loads(data)["id"]

    get_headers = { 'x-api-key': API_KEY }

    state = "new"
    result = {}
    while not (state == "done" or state == "error"):
        time.sleep(1)
        conn.request("GET", f"/file-processing/jobs/{job_id}", headers=get_headers)
        res = conn.getresponse()
        data = res.read()
        result = json.loads(data)
        state = result["state"]
        print("Job configuration:", result["config"])
        print("Job state:", state)
        if state == "error":
            print("There was an error: ", result["error_description"])
        if state == "done":
            conn.request("GET", f"/file-processing/jobs/{job_id}/results", headers=get_headers)
            res = conn.getresponse()
            data = res.read()
            result = json.loads(data)["result"]
            print(result)

    print("Time series:")
    for ts_result in result["channels"]["0"]["time_series"]:
        ts = ts_result["timestamp"]
        res = ts_result["results"]["emotions"]
        print(f'Timestamp: {ts}ms\tresult: {res["result"]}\t'
                f'confidence: {res["confidence"]}')

#    print("\nRaw model outputs:")
#    for ts_result in result["channels"]["0"]["time_series"]:
#        ts = ts_result["timestamp"]
#        raw = ts_result["raw"]["gender"]
#        print(f'Timestamp: {ts}ms\traw results: male: ' 
#              f'{raw["male"]}, female: {raw["female"]}')

    summary = result["channels"]["0"]["summary"]["emotions"]
    happy = summary["happy_fraction"] * 100
    tired = summary["tired_fraction"] * 100
    neutral = summary["neutral_fraction"] * 100
    silence = summary["silence_fraction"] * 100
    irritated = summary["irritated_fraction"] * 100
    no_speech = summary["no_speech_fraction"] * 100
    print(f'\nSummary:  happy: {happy}%, tired: {tired}%, neutral: {neutral}%, silence: {silence}%, irritated: {irritated}%, no_speech: {no_speech}%')

#    print("\nTransitions:")
#    for ts_result in result["channels"]["0"]["transitions"]["emotions"]:
#        ts = ts_result["timestamp_start"]
#        print(f'Timestamp: {ts}ms\tresult: {ts_result["result"]}\t'
#                f'confidence: {ts_result["confidence"]}')

    result = [file, happy, tired, neutral, silence, irritated, no_speech]
    return result

if __name__ == "__main__":
    main()

