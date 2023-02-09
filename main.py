import datetime
import docx
import json
import math
import os
from docx import Document
import timecode as tc


def is_float(value):
  try:
    float(value)
    return True
  except:
    return False


def get_smpte_frames(time, framerate, smpte_timecode):
	seconds = int(math.floor(time))
	hours  = seconds // 3600
	minutes = (seconds % 3600) // 60
	seconds = seconds % 60
	frame_float = float(time) - int(math.floor(time))
	frames = int(math.floor(frame_float * float(framerate)))
	tc1 = tc.Timecode(framerate, str(hours)+":"+str(minutes)+":"+str(seconds)+":"+str(frames))
	if smpte_timecode != None:
		tc2 = tc.Timecode(framerate, str(smpte_timecode[0])+":"+str(smpte_timecode[1])+":"+str(smpte_timecode[2])+":"+str(smpte_timecode[3]))
		tc3 = tc1 + tc2
		print(tc3)
		#[timecode_hours, timecode_mins, timecode_secs, timecode_frames]
		#seconds = seconds + int(smpte_timecode[2]) 
		#hours = hours + int(smpte_timecode[0])
		#minutes = minutes + int(smpte_timecode[1])
		return str(tc3)
	else:
		return str(hours).zfill(2)+":"+ str(minutes).zfill(2)+":"+str(seconds).zfill(2)+":"+str(frames).zfill(2)

	#return str(hours).zfill(2)+":"+ str(minutes).zfill(2)+":"+str(seconds).zfill(2)+":"+str(frames).zfill(2)

def get_smpte_milli(time, smpte_timecode):
	seconds = int(math.floor(time))
	hours  = seconds // 3600
	minutes = (seconds % 3600) // 60
	seconds = seconds % 60
	frame_float = float(time) - int(math.floor(time))
	if smpte_timecode != None:
		seconds_millis = float(seconds) + float(frame_float) + float(smpte_timecode[2]) + float(smpte_timecode[3])
		seconds_millis_ints = str(seconds_millis).split(".")[0]
		seconds_millis_float = str(seconds_millis).split(".")[1]
		rounded_minute = int(seconds_millis_ints) // 60
		seconds = int(seconds_millis_ints) % 60 #modulo 60 to get remainder
		minutes = int(minutes) + int(rounded_minute) + int(smpte_timecode[1])
		rounded_hour = int(minutes) // 60
		minutes = int(minutes) % 60
		hours = int(hours) + int(smpte_timecode[0]) + int(rounded_hour)
		sm_comma = str(seconds).zfill(2) + "," + seconds_millis_float.zfill(3)[:3]
	
		return str(hours).zfill(2)+":"+ str(minutes).zfill(2)+":"+str(sm_comma)




	else:
		seconds_millis = float(seconds) + float(frame_float)
		#sm_comma = str(seconds_millis).replace(".", ",")
		seconds_millis_ints = str(seconds_millis).split(".")[0]
		seconds_millis_float = str(seconds_millis).split(".")[1]

		sm_comma = seconds_millis_ints.zfill(2) + "," + seconds_millis_float.zfill(3)[:3]

		return str(hours).zfill(2)+":"+ str(minutes).zfill(2)+":"+str(sm_comma)


def get_gaps(framerate, framerate_choice, output_text, output_csv, file):
	global gap_count
	g_thresh = input("Please type a gap threshold: ")
	try:
		if g_thresh.isdigit():
			threshold_choice = True
			gap_duration = float(g_thresh)
			time = 0.0
			word = ""
			previous_words = []

			if output_text:
				filename, file_extension = os.path.splitext(file)
				f = open(filename+".srt","w+", encoding="utf8")
			
			if output_csv:
				filename, file_extension = os.path.splitext(file)
				c = open(filename+".csv","w+", encoding="utf8")
				c.write("Input Timecode,Output Timecode,Dialogue,Max time in ms\n")
			
			count = 0

			for key, value in enumerate(data["results"]):
				word = value["alternatives"][0]["content"]
				if len(previous_words) == 5:
					del previous_words[0]
					previous_words.append(word)
				else:
					previous_words.append(word)

				gap = float(value["start_time"]) - time
				gap_decimal = str(gap).split(".")[1]
				gap_int = str(gap).split(".")[0]
				gap = float(str(gap_int) + "." + str(gap_decimal[:3]))
				if gap > gap_duration:
					gap_count += 1
					#start_time = round(time/60, 2)
					start_time = datetime.timedelta(seconds=float(time))
					end_time = datetime.timedelta(seconds=float(value["start_time"]))

					print("\n*****Audio gap found*****")
					if count == 0:
						p.add_run("*****Audio gap found*****")
					else:
						p.add_run("\n\n*****Audio gap found*****")
					print("Previous words: " + ' '.join(previous_words))
					p.add_run("\nPrevious words: " + ' '.join(previous_words))
					
					if framerate_choice == False:
						print("Start: "+str(get_smpte_milli(time, smpte_timecode)))
						p.add_run("\nStart: "+str(get_smpte_milli(time, smpte_timecode)))
						print("End: "+str(get_smpte_milli(float(value["start_time"]), smpte_timecode)))
						p.add_run("\nEnd: "+str(get_smpte_milli(float(value["start_time"]), smpte_timecode)))
					else:
						print("Start TC: "+get_smpte_frames(time, framerate, smpte_timecode))
						p.add_run("\nStart TC: "+get_smpte_frames(time, framerate, smpte_timecode))
						print("End TC: "+get_smpte_frames(float(value["start_time"]), framerate, smpte_timecode))
						p.add_run("\nEnd TC: "+get_smpte_frames(float(value["start_time"]), framerate, smpte_timecode))

					print("Duration: "+str(gap) + " seconds")
					p.add_run("\nDuration: "+str(gap) + " seconds")


					if output_text:
						f.write(str(gap_count) +"\n")
						if framerate_choice == False: 
							f.write(str(get_smpte_milli(time, smpte_timecode))+" --> "+str(get_smpte_milli(float(value["start_time"]), smpte_timecode))+"\n")
						else:
							f.write(str(get_smpte_frames(time, framerate, smpte_timecode))+" --> "+str(get_smpte_frames(float(value["start_time"]), framerate, smpte_timecode))+"\n")
						f.write(' '.join(previous_words)+"\n\n")
					if output_csv:
						#c.write(str(gap_count) +"\n")
						if framerate_choice == False: 
							c.write('"' + str(get_smpte_milli(time, smpte_timecode)) + '","' + 
									str(get_smpte_milli(float(value["start_time"]), smpte_timecode)) + '",' +
									' '.join(previous_words) + ',' + str(int(gap*1000)) + "\n")
						else:
							c.write('"' + str(get_smpte_frames(time, framerate, smpte_timecode)) + '","' + 
									str(get_smpte_frames(float(value["start_time"]), framerate, smpte_timecode)) + '",' +
									' '.join(previous_words) + ',' + str(int(gap*1000)) + "\n")
						

				time = float(value["start_time"])
				count += 1

			if output_text:
				f.close()

		
	except Exception as e:
		print(e)



gap_count = 0
document = Document()
p = document.add_paragraph("")
input_folder = os.getcwd() + "\\input\\"

if not os.path.exists(input_folder):
   os.makedirs(input_folder)

if len(os.listdir(input_folder)) == 0:
	print("Please put a file into the input folder")

for file in os.listdir(input_folder):
	with open(input_folder + file, encoding="utf8") as f:
		data = json.load(f)

	threshold_choice = False
	output_text = False
	output_csv = False
	framerate_choice = False
	output_docx = False

	#commands
	while threshold_choice is False:
		framerate = input("Do you want your results in SMPTE timecode? (Y / N) ")
		if framerate.lower() == "y" or framerate.lower() == "yes":
			framerate_choice = True

			get_start_timecode = input("Do you know the start timecode? ")
			if get_start_timecode.lower() == "y" or get_start_timecode.lower() == "yes":
				get_start_timecode = True
			

				timecode_hours = input("Please enter the start timecodes hours value: ")
				if timecode_hours.isdigit():
					pass
				else:
					print("I don't understand " + str(timecode_hours))
					print("closing...")
					exit()
				timecode_mins = input("Please enter the start timecodes minutes value: ")
				if timecode_mins.isdigit():
					pass
				else:
					print("I don't understand " + str(timecode_mins))
					print("closing...")
					exit()
				timecode_secs = input("Please enter the start timecodes seconds value: ")
				if timecode_secs.isdigit():
					pass
				else:
					print("I don't understand " + str(timecode_secs))
					print("closing...")
					exit()
				timecode_frames = input("Please enter the start timecodes frames value: ")
				if timecode_frames.isdigit():
					pass
				else:
					print("I don't understand " + str(timecode_frames))
					print("closing...")
					exit()

				smpte_timecode = [timecode_hours, timecode_mins, timecode_secs, timecode_frames]

			else:
				smpte_timecode = None
				get_start_timecode = False

			display_framerate = input("Please type the framerate: ")

			if is_float(display_framerate):
				display_framerate = float(display_framerate)
			else:
				display_framerate = int(display_framerate)

			if type(display_framerate) is float or type(display_framerate) is int:
				output_text_choice = input("Do you want to output an srt file? (Y / N) ")
				if output_text_choice.lower() == "y" or output_text_choice.lower() == "yes":
					output_text = True
				else:
					output_text = False
			else:
				print("I don't understand " + str(input) + " please type a number and try again")
			
			output_docx_choice = input("Do you want to output a docx file? (Y / N) ")
			if output_docx_choice.lower() == "y" or output_docx_choice.lower() == "yes":
				output_docx = True
			else:
				output_docx = False

			output_csv_choice = input("Do you want to output a csv file? (Y / N) ")
			if output_csv_choice.lower() == "y" or output_csv_choice.lower() == "yes":
				output_csv = True
			else:
				output_csv = False
				
		else:
			framerate_choice = False
			display_framerate = 0

			get_start_timecode = input("Do you know the start timecode? ")
			if get_start_timecode.lower() == "y" or get_start_timecode.lower() == "yes":
				get_start_timecode = True
			

				timecode_hours = input("Please enter the start timecodes hours value: ")
				if timecode_hours.isdigit():
					pass
				else:
					print("I don't understand " + str(timecode_hours))
					print("closing...")
					exit()
				timecode_mins = input("Please enter the start timecodes minutes value: ")
				if timecode_mins.isdigit():
					pass
				else:
					print("I don't understand " + str(timecode_mins))
					print("closing...")
					exit()
				timecode_secs = input("Please enter the start timecodes minutes value: ")
				if timecode_secs.isdigit():
					pass
				else:
					print("I don't understand " + str(timecode_secs))
					print("closing...")
					exit()
				timecode_frames = input("Please enter the start timecodes frames value: ")
				if timecode_frames.isdigit():
					pass
				else:
					print("I don't understand " + str(timecode_frames))
					print("closing...")
					exit()

				smpte_timecode = [timecode_hours, timecode_mins, timecode_secs, timecode_frames]

			else:
				smpte_timecode = None
				get_start_timecode = False

			output_text_choice = input("Do you want to output an srt file? (Y / N) ")
			if output_text_choice.lower() == "y" or output_text_choice.lower() == "yes":
				output_text = True
			else:
				output_text = False

			output_docx_choice = input("Do you want to output a docx file? (Y / N) ")
			if output_docx_choice.lower() == "y" or output_docx_choice.lower() == "yes":
				output_docx = True
			else:
				output_docx = False

			output_csv_choice = input("Do you want to output a csv file? (Y / N) ")
			if output_csv_choice.lower() == "y" or output_csv_choice.lower() == "yes":
				output_csv = True
			else:
				output_csv = False

		threshold_choice = True
		get_gaps(display_framerate, framerate_choice, output_text, output_csv, file)

	print("\nTotal number of gaps in the JSON: " + str(gap_count))
	p.add_run("\nTotal number of gaps in the JSON: " + str(gap_count))

	if output_docx:
		filename, file_extension = os.path.splitext(file)
		document.save(filename + '.docx')
	else:
		pass

	#print(str(key["name"]))
		#for words in d:
			#for a in words:
				#print(a)

input()