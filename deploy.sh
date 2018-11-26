#!/bin/bash
zip -r robocar-ai_v1.zip donkeycar setup.py
ssh pi@blown302.local 'cd robocar && rm -r donkeycar setup.py'
scp robocar-ai_v1.zip pi@blown302.local:~/robocar/
rm robocar-ai_v1.zip
ssh pi@blown302.local 'cd robocar && unzip robocar-ai_v1.zip && rm robocar-ai_v1.zip'