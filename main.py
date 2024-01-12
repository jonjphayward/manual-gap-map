import datetime
import json
import math
import os
from docx import Document
import timecode as tc

def is_float(value):
    """Check if a value can be converted to float."""
    try:
        float(value)
        return True
    except ValueError:
        return False

def get_smpte_frames(time, framerate, smpte_timecode):
    # Check if the framerate is one of the drop frame rates
    drop_frame = framerate in [23.976, 23.98, 29.97]

    if drop_frame:
        # Adjust framerate for drop frame calculation
        if framerate in [23.976, 23.98]:
            adjusted_fps = 24 * (1000 / 1001)
        elif framerate == 29.97:
            adjusted_fps = 30 * (1000 / 1001)

        # Calculate total frames based on adjusted fps
        total_frames = int(round(time * adjusted_fps))
        frames = total_frames % round(adjusted_fps)
        total_seconds = total_frames // round(adjusted_fps)
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60
        hours = total_minutes // 60
    else:
        # Calculate time for non-drop frame rates
        seconds = int(math.floor(time))
        hours  = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        frame_float = float(time) - int(math.floor(time))
        frames = int(math.floor(frame_float * float(framerate)))

    tc1 = tc.Timecode(framerate, f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}")

    if smpte_timecode is not None:
        tc2 = tc.Timecode(framerate, f"{smpte_timecode[0]:02}:{smpte_timecode[1]:02}:{smpte_timecode[2]:02}:{smpte_timecode[3]:02}")
        tc3 = tc1 + tc2
        return str(tc3)
    else:
        return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

def get_smpte_milli(time, smpte_timecode):
    seconds = int(math.floor(time))
    hours  = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    frame_float = float(time) - int(math.floor(time))

    if smpte_timecode is not None:
        seconds_millis = float(seconds) + frame_float + float(smpte_timecode[2]) + float(smpte_timecode[3])
        seconds_millis_ints = str(seconds_millis).split(".")[0]
        seconds_millis_float = str(seconds_millis).split(".")[1]
        rounded_minute = int(seconds_millis_ints) // 60
        seconds = int(seconds_millis_ints) % 60
        minutes = minutes + rounded_minute + int(smpte_timecode[1])
        rounded_hour = minutes // 60
        minutes = minutes % 60
        hours = hours + int(smpte_timecode[0]) + rounded_hour
        sm_comma = str(seconds).zfill(2) + "," + seconds_millis_float.zfill(3)[:3]
    else:
        seconds_millis = float(seconds) + frame_float
        seconds_millis_ints = str(seconds_millis).split(".")[0]
        seconds_millis_float = str(seconds_millis).split(".")[1]
        sm_comma = seconds_millis_ints.zfill(2) + "," + seconds_millis_float.zfill(3)[:3]

    return str(hours).zfill(2) + ":" + str(minutes).zfill(2) + ":" + sm_comma


def get_gaps(framerate, is_framerate_choice, output_text, output_csv, file_path, smpte_timecode, data):
    """Process gaps in speech based on the given parameters."""
    gap_count = 0
    document = Document()
    paragraph = document.add_paragraph("")

    g_thresh = input("Please type a gap threshold: ")
    if not g_thresh.isdigit():
        raise ValueError("Threshold must be a number.")

    gap_duration = float(g_thresh)
    time = 0.0
    previous_words = []

    # File operations for output
    filename, file_extension = os.path.splitext(file_path)
    file_handlers = open_output_files(output_text, output_csv, filename)

    for key, value in enumerate(data["results"]):
        word = value["alternatives"][0]["content"]
        if len(previous_words) == 5:
            del previous_words[0]
        previous_words.append(word)

        gap = float(value["start_time"]) - time
        if gap > gap_duration:
            gap_count += 1
            start_time = datetime.timedelta(seconds=float(time))
            end_time = datetime.timedelta(seconds=float(value["start_time"]))

            paragraph.add_run(f"\n\n*****Audio gap found*****\nPrevious words: {' '.join(previous_words)}\n")
            if is_framerate_choice:
                paragraph.add_run(f"Start TC: {get_smpte_frames(time, framerate, smpte_timecode)}\n")
                paragraph.add_run(f"End TC: {get_smpte_frames(float(value['start_time']), framerate, smpte_timecode)}\n")
            else:
                paragraph.add_run(f"Start: {get_smpte_milli(time, smpte_timecode)}\n")
                paragraph.add_run(f"End: {get_smpte_milli(float(value['start_time']), smpte_timecode)}\n")
            paragraph.add_run(f"Duration: {gap} seconds")

            if output_text:
                text_file = file_handlers.get("text_file")
                text_file.write(f"{gap_count}\n")
                if is_framerate_choice:
                    text_file.write(f"{get_smpte_frames(time, framerate, smpte_timecode)} --> {get_smpte_frames(float(value['start_time']), framerate, smpte_timecode)}\n")
                else:
                    text_file.write(f"{get_smpte_milli(time, smpte_timecode)} --> {get_smpte_milli(float(value['start_time']), smpte_timecode)}\n")
                text_file.write(f"{' '.join(previous_words)}\n\n")

            if output_csv:
                csv_file = file_handlers.get("csv_file")
                if is_framerate_choice:
                    csv_file.write(f'"{get_smpte_frames(time, framerate, smpte_timecode)}","{get_smpte_frames(float(value["start_time"]), framerate, smpte_timecode)}","{" ".join(previous_words)}",{int(gap*1000)}\n')
                else:
                    csv_file.write(f'"{get_smpte_milli(time, smpte_timecode)}","{get_smpte_milli(float(value["start_time"]), smpte_timecode)}","{" ".join(previous_words)}",{int(gap*1000)}\n')

        time = float(value["start_time"])

    close_output_files(file_handlers)
    return gap_count, document

def open_output_files(output_text, output_csv, filename):
    """Open file handlers for output files."""
    handlers = {}
    if output_text:
        handlers["text_file"] = open(filename + ".srt", "w+", encoding="utf8")
    if output_csv:
        handlers["csv_file"] = open(filename + ".csv", "w+", encoding="utf8")
        handlers["csv_file"].write("Input Timecode,Output Timecode,Dialogue,Max time in ms\n")
    return handlers

def close_output_files(handlers):
    """Close opened file handlers."""
    for handler in handlers.values():
        handler.close()

def get_user_preferences():
    """Get user preferences for timecode and framerate."""
    smpte_timecode = None
    framerate_choice = input("Do you want your results in SMPTE timecode? (Y / N) ").lower() in ["y", "yes"]
    framerate = 0

    if framerate_choice:
        smpte_timecode = get_start_timecode()
        framerate = get_framerate()
    else:
        # If SMPTE timecode is not chosen, then default to hours:minutes:seconds.milliseconds format
        smpte_timecode = [0, 0, 0, 0]  # Default start timecode

    return smpte_timecode, framerate, framerate_choice

def get_start_timecode():
    """Get start timecode from the user."""
    get_start_timecode = input("Do you know the start timecode? (Y / N) ").lower() in ["y", "yes"]
    if get_start_timecode:
        timecode_hours = get_validated_input("Please enter the start timecode's hours value: ", int)
        timecode_mins = get_validated_input("Please enter the start timecode's minutes value: ", int)
        timecode_secs = get_validated_input("Please enter the start timecode's seconds value: ", int)
        timecode_frames = get_validated_input("Please enter the start timecode's frames value: ", int)

        return [timecode_hours, timecode_mins, timecode_secs, timecode_frames]
    return None

def get_framerate():
    """Get framerate from the user."""
    while True:
        display_framerate = input("Please type the framerate: ")
        if is_float(display_framerate):
            return float(display_framerate)
        else:
            print("Invalid input. Please type a numeric framerate.")

def get_output_preferences():
    """Get user preferences for output file formats."""
    output_text = input("Do you want to output an srt file? (Y / N) ").lower() in ["y", "yes"]
    output_docx = input("Do you want to output a docx file? (Y / N) ").lower() in ["y", "yes"]
    output_csv = input("Do you want to output a csv file? (Y / N) ").lower() in ["y", "yes"]

    return output_text, output_docx, output_csv

def get_validated_input(prompt, input_type):
    """Get validated input of a specific type from the user."""
    while True:
        user_input = input(prompt)
        try:
            return input_type(user_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")

def main():
    """Main function to run the script."""
    input_folder = os.path.join(os.getcwd(), "input")
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    if not os.path.exists(input_folder) or not os.listdir(input_folder):
        print("Please put a file into the input folder")
        return

    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)
        with open(file_path, encoding="utf8") as f:
            data = json.load(f)

        smpte_timecode, framerate, is_framerate_choice = get_user_preferences()
        output_text, output_docx, output_csv = get_output_preferences()

        gap_count, document = get_gaps(framerate, is_framerate_choice, output_text, output_csv, file_path, smpte_timecode, data)

        print(f"\nTotal number of gaps in the JSON: {gap_count}")
        if output_docx:
            filename = os.path.splitext(file_path)[0]
            document.save(filename + '.docx')

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
