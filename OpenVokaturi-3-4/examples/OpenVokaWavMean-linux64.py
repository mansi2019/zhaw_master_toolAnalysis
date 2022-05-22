# OpenVokaWavMean-linux64.py
# public-domain sample code by Vokaturi, 2020-02-20
#
# A sample script that uses the VokaturiPlus library to extract the emotions from
# a wav file on disk. The file has to contain a mono recording.
#
# This script has been extended in order to analyze EMO-DB dataset and save results for further processing


import sys
import scipy.io.wavfile
import pandas as pd
import os


sys.path.append("../api")
import Vokaturi

def main():
	print ("Loading library...")
	Vokaturi.load("../lib/open/linux/OpenVokaturi-3-4-linux64.so")
	print ("Analyzed by: %s" % Vokaturi.versionAndLicense())

	results = []
	results.append(["filename", "happy_percentage", "sadness_percentage", "neutral_percentage", "anger_percentage", "fear_percentage"])

	directory = os.fsencode('/home/singhma3/masterarbeit/wav/')

	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		if filename.endswith(".wav"):
			filepath = directory+file
			result = get_vokaturi_emotions(filepath, file)
			results.append(result)
		else:
			print("Skip" + file)   
    
	df = pd.DataFrame(results)
	df.to_csv('vokaturi_results.csv',index=False)



def get_vokaturi_emotions(file_name, file):
	print ("Reading sound file...")
	(sample_rate, samples) = scipy.io.wavfile.read(file_name)
	print ("   sample rate %.3f Hz" % sample_rate)

	print ("Allocating Vokaturi sample array...")
	buffer_length = len(samples)
	print ("   %d samples, %d channels" % (buffer_length, samples.ndim))
	c_buffer = Vokaturi.SampleArrayC(buffer_length)
	if samples.ndim == 1:  # mono
		c_buffer[:] = samples[:] / 32768.0
	else:  # stereo
		c_buffer[:] = 0.5*(samples[:,0]+0.0+samples[:,1]) / 32768.0

	print ("Creating VokaturiVoice...")
	voice = Vokaturi.Voice (sample_rate, buffer_length)

	print ("Filling VokaturiVoice with samples...")
	voice.fill(buffer_length, c_buffer)

	print ("Extracting emotions from VokaturiVoice...")
	quality = Vokaturi.Quality()
	emotionProbabilities = Vokaturi.EmotionProbabilities()
	voice.extract(quality, emotionProbabilities)

	if quality.valid:
		neutral_percentage =emotionProbabilities.neutrality
		happy_percentage = emotionProbabilities.happiness
		sadness_percentage = emotionProbabilities.sadness
		anger_percentage = emotionProbabilities.anger
		fear_percentage = emotionProbabilities.fear

		print ("Neutral: %.3f" % emotionProbabilities.neutrality)
		print ("Happy: %.3f" % emotionProbabilities.happiness)
		print ("Sad: %.3f" % emotionProbabilities.sadness)
		print ("Angry: %.3f" % emotionProbabilities.anger)
		print ("Fear: %.3f" % emotionProbabilities.fear)
	else:
		neutral_percentage = 0
		happy_percentage = 0
		sadness_percentage = 0
		anger_percentage = 0
		fear_percentage = 0
		print ("Not enough sonorancy to determine emotions")

	voice.destroy()

	result = [file, happy_percentage, sadness_percentage, neutral_percentage, anger_percentage, fear_percentage]
	return result

if __name__ == "__main__":
    main()
