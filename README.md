## manual-gap-map

The Gap Map tool takes the output from speechmatics (json) and converts it to a srt file formatted to highlight the pauses in the dialogue.

#### Instructions:
I have converted the python script to an exe file with everything you need to get started in the zip folder.
1) Download the git repository
2) Extract the gap-map.zip
3) Once extracted you should see a folder system like this:
.
├── ...
├── gap-map/
│   ├── package/
│   ├── ├── input/
│   ├── ├── main.exe
└── ...
4) Copy your speechmatic json files into the input folder and then double click the main.exe file.

Instructions will appear in the terminal


#### Planned updates:

Removing the need for human input by adding the info into the filename:

<table><tbody><tr><td>Filename</td><td>testfile.json</td></tr><tr><td>Starting timecode</td><td>10:00:00:00</td></tr><tr><td>Framerate</td><td>25 fps</td></tr><tr><td>Gap duration</td><td>5 seconds</td></tr></tbody></table>

For the example above the user should append the filename with each number separated with a = character ie:  
testfile.json → testfile=10000000=25=5.json

For multiple files they can all be added to the input and run in a batch.