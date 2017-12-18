# HoI4TransferTechnologySEGenerator
HoI 4 Transfer Technology scripted effect generator by Yard1, originally for Equestria at War mod.

Written in Python 2.7

Transfer Technology scripted effect will grant all techs researched by PREV to ROOT

Best used when ROOT is just spawned (eg. as a civil war TAG)

It is not advised to use this for already existing nations, as mutually exclusive techs will be given regardless of what ROOT has already researched

Copyright (c) 2017 Antoni Baum (Yard1)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


usage: hoi4transfertechsegen.py [-h] [-en effectname] [-a | -o] input output

Given an input technology file or folder, generate a Transfer Technology
scripted effect.

positional arguments:
  
  input                 Technology file name/folder containing files
  
  output                File name to write the scripted effect to


optional arguments:
  
  -h, --help            show this help message and exit
  
  -en effectname, --effectname effectname
                        Name of the scripted effect
                        (default:"transfer_technology")
  
  -a, --add             Will add new technologies to an already existing
                        transfer_technology effect (first set name with -en)
  
  -o, --overwrite       Will overwrite the output file if it already exists
