# clocker
Clocker is a CLI application that can record and view work hours. It is written using the argparse module from Python. It is used to record and view work hours.

usage: clocker.py [-h] [-i | -o] [-w | -b | -l] [-rm REMOVE [REMOVE ...] | --clear] [-t] [-d]

track your work hours by clocking in and out

optional arguments:
  -h, --help            show this help message and exit
  -i, --in              set action as clocking in
  -o, --out             set action as clocking out
  -w, --work            set task as work
  -b, --break           set task as break
  -l, --lunch           set task as lunch
  -r REMOVE [REMOVE ...], --remove REMOVE [REMOVE ...]
                        remove the i_th record
  --clear               remove all clock records
  -t, --today           display a summary of today's work
  -k, --week            display a summary of this week's work
  -d, --display         display work clock records