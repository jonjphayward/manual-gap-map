# manual-gap-map

The Gap Map tool takes the output from speechmatics (json) and converts it to a srt file formatted to highlight the pauses in the dialogue.


Planned updates:
Removing need for human input by having info in filename:

Filename                testfile.json
Starting timecode       10:00:00:00
Framerate               25 fps
Gap duration            5 seconds

For the example above the user should append the filename with each number separated with a = character ie:
testfile.json
testfile=10000000=25=5.json

For multiple files they can all be added to the input and run in a batch.