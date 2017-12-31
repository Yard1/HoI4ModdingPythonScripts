#!/usr/bin/python
import argparse
import os
import sys
import re

#############################
###
### HoI 4 Localisation Adder by Yard1, originally for Equestria at War mod
### Written in Python 2.7
###
### Copyright (c) 2017 Antoni Baum (Yard1)
### Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
### The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
### THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
###
### usage: hoi4localisationadder.py [-h] [-t] input output
### 
### Given an event, national_focus or ideas file, add missing localisation entries
### to a specified localisation file. Note: custom tooltips are not supported. In
### case of events, title, description and option names will be added (triggered
### titles and descriptions are supported). For national_focus and ideas, names
### and descriptions will be added.
### 
### positional arguments:
###   input       Event, national_focus or ideas file to parse
###   output      Localisation file to write to (if empty/non-existing, a new
###               English localisation file will be created)
### 
### optional arguments:
###   -h, --help  show this help message and exit
###   -t, --todo  Add "#TODO" to every added line instead of just once (Default:
###               False)
### 
#############################
def readfile(name):
    print("Reading file " + name + "...")
    with open(name, "r") as f:
        lines = f.read().splitlines()
    tags = list()

    open_blocks = 0
    is_event_file = False
    is_focus_file = False
    is_idea_file = False
    for line in lines:
        line = re.sub('#.*', "", line)
        if not is_event_file and not is_focus_file and not is_idea_file:
            if "focus_tree" in line:
                is_focus_file = True
                print("File " + name + " is a national_focus file...")
            elif "add_namespace" in line:
                is_event_file = True
                print("File " + name + " is an event file...")
            elif "ideas" in line:
                is_idea_file = True
                print("File " + name + " is an ideas file...")
        if is_focus_file:
            if open_blocks == 2 and re.match('^.*id ?=', line):
                temp_line = re.sub('^.*id ?=', "", line)
                temp_line = re.sub('\s', "", temp_line)
                temp_line.strip()
                tags.append(temp_line)
        elif is_idea_file:
            if open_blocks == 2 and "{" in line:
                temp_line = line
                temp_line = re.sub('\s|=(\s|){', "", temp_line)
                temp_line.strip()
                tags.append(temp_line)
        elif is_event_file:
            if open_blocks > 0 and open_blocks < 3 and re.match('^.*(title|desc|name|text) ?=', line):
                temp_line = re.sub('^.*(title|desc|name|text) ?=', "", line)
                temp_line = re.sub('\s', "", temp_line)
                temp_line.strip()
                tags.append(temp_line)
        open_blocks += line.count('{')
        open_blocks -= line.count('}')

    print("File " + name + " read successfully!")
    return tags, (is_event_file, is_focus_file, is_idea_file)
###################################################################
parser = argparse.ArgumentParser(description='Given an event, national_focus or ideas file, add missing localisation entries to a specified localisation file. Note: custom tooltips are not supported. In case of events, title, description and option names will be added (triggered titles and descriptions are supported). For national_focus and ideas, names and descriptions will be added.')
parser.add_argument('input', metavar='input',
                    help='Event, national_focus or ideas file to parse')
parser.add_argument( 'output', metavar='output',
                    help='Localisation file to write to (if empty/non-existing, a new English localisation file will be created)')
parser.add_argument( '-t', '--todo', action='store_true',
                    help='Add "#TODO" to every added line instead of just once (Default: False)')

args = parser.parse_args()

parsed_file = readfile(args.input)
if not parsed_file[1][0] and not parsed_file[1][1] and not parsed_file[1][2:]:
    sys.exit("File " + args.input + " is not a valid event, national_focus or ideas file.")
lines = list()
with open(args.output,"r") as f:
    lines = f.read().splitlines()
if len(lines) < 1:
    print("Output file " + args.output + " is empty or doesn't exist, creating a new english localisation file.")
    lines.append("l_english:")
for line in lines:
    for i,parsed_line in enumerate(parsed_file[0]):
        if parsed_line in line:
            print(parsed_line + " already in output file, skipping")
            parsed_file[0].remove(parsed_file[0][i])
output_lines = list()
if len(parsed_file[0]) > 0:
    if not args.todo:
        output_lines.append("\n #TODO")
    else:
        output_lines.append("\n")
    for line in parsed_file[0]:
        if args.todo:
            output_lines.append(" #TODO")
        output_lines.append(" " + line + ":0 \"\"")
        if parsed_file[1][1] or parsed_file[1][2]:
            output_lines.append(" " + line + "_desc:0 \"\"")
    with open(args.output,"a") as f:
        f.writelines(str(line) + "\n" for line in output_lines)
print("Appended " + str(len(parsed_file[0])) + " lines to output file " + args.output + " successfully!")
