#!/usr/bin/python3
import argparse
import os
import sys
import re
from collections import defaultdict
import random
import pickle
import traceback
import itertools
import colorsys

try:
    import p_tqdm
    from tqdm import tqdm
except:
    sys.exit("Requires p_tqdm pip package to be installed. Run:\npip install p_tqdm\nor\npip3.6 install p_tqdm\ndepending on your installation and start the script again.\nMore info on installing packages: https://docs.python.org/3/installing/index.html")

try:
    from PIL import Image, ImageDraw, ImageFont
except:
    sys.exit("Requires pillow pip package to be installed. Run:\npip install pillow\nor\npip3.6 install pillow\ndepending on your installation and start the script again.\nMore info on installing packages: https://docs.python.org/3/installing/index.html")

try:
    import numpy as np
except:
    sys.exit("Requires numpy pip package to be installed. Run:\npip install numpy\nor\npip3.6 install numpy\ndepending on your installation and start the script again.\nMore info on installing packages: https://docs.python.org/3/installing/index.html")

try:
    import seaborn as sns
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except:
    sys.exit("Requires seaborn pip package to be installed. Run:\npip install seaborn\nor\npip3.6 install seaborn\ndepending on your installation and start the script again.\nMore info on installing packages: https://docs.python.org/3/installing/index.html")


#############################
###
### HoI 4 State IDs Map Generator by Yard1, originally for Equestria at War mod
### Written in Python 3.6
### Requires p_tqdm, pillow and numpy pip packages to be installed. More info on installing packages: https://docs.python.org/3/installing/index.html
###
### Copyright (c) 2018 Antoni Baum (Yard1)
### Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
### The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
### THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
###
### usage: hoi4statemapgenerator.py [-h] [-c COLORS] [-f FONT] [-nid]
###                                 mode provinces definition states output
###
### Given valid provinces.bmp, definition.csv files and a folder of state history
### files (or strategic region files), generate an image containing a map of
### states with their IDs.
###
### positional arguments:
###   mode                  Mode: 0 - states, 1 - population per pixel, 2 -
###                         political, 3 - total factories, 4 - civ factories, 5 -
###                         mil factories, 6 - infra, 7 - nav factories
###   provinces             Path to provinces.bmp file
###   definition            Path to definition.csv file
###   states                Path to 'history/states' or 'map/strategicregions'
###                         folder
###   output                Name of output file
###
### optional arguments:
###   -h, --help            show this help message and exit
###   -c COLORS, --colors COLORS
###                         Name of pregenerated colors.pickle file (Default:
###                         hoi4statemapgenerator_colors.pickle)
###   -f FONT, --font FONT  Name of font to use (Default: ARIALN.TTF)
###   -nid, --no_ids        Do not put IDs on the map (Default: False)
###
#############################

BLUE_RBG = (68, 107, 163)
MANPOWER_STEPS = 10

def readable_dir(prospective_dir):
  if not os.path.isdir(prospective_dir):
    raise Exception("readable_dir:{0} is not a valid path".format(prospective_dir))
  if os.access(prospective_dir, os.R_OK):
    return prospective_dir
  else:
    raise Exception("readable_dir:{0} is not a readable dir".format(prospective_dir))

#############################

# Copyright 2011 Álvaro Justen [alvarojusten at gmail dot com]
# License: GPL <http://www.gnu.org/copyleft/gpl.html>
# Begin copyright

def get_random_color(pastel_factor = 0.5):
    return [(x+pastel_factor)/(1.0+pastel_factor) for x in [random.uniform(0,1.0) for i in [1,2,3]]]

def color_distance(c1,c2):
    return sum([abs(x[0]-x[1]) for x in zip(c1,c2)])

def generate_new_color(existing_colors,pastel_factor = 0.5):
    max_distance = None
    best_color = None
    for _ in range(0,100):
        color = get_random_color(pastel_factor = pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color,c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color

# End copyright

#############################

providstate = {}

class State():
    def __init__(self, state_id, provinces, manpower, owner, category, industrial_complex=0, arms_factory=0, infrastructure=0, dockyard=0):
        self.state_id = state_id
        self.provinces = provinces
        self.manpower = manpower
        self.owner = owner
        self.category = category
        self.industrial_complex = industrial_complex
        self.arms_factory = arms_factory
        self.infrastructure = infrastructure
        self.dockyard = dockyard
        self.pixels = 0
        for province in provinces:
            providstate[province] = self

def load_provinces(name):
    print("Reading file " + name + "...")
    im = Image.open(name)
    return im

def load_definition(name):
    print("Reading file " + name + "...")
    try:
        with open(name, "r") as f:
            lines = f.read().splitlines()
    except:
        try:
            with open(name, "r", encoding='utf-8') as f:
                lines = f.read().splitlines()
        except:
            try:
                with open(name, "r", encoding='utf-8-sig') as f:
                    lines = f.read().splitlines()
            except Exception as e:
                print("Could not read file " + name + "!")
                print(e)
    provinces = {}
    provinces_rev = {}
    for line in lines:
        line = line.split(";")
        provinces[int(line[0])] = (int(line[1]), int(line[2]), int(line[3]))
        provinces_rev[(int(line[1]), int(line[2]), int(line[3]))] = int(line[0])
    return (provinces, provinces_rev)

def load_state_file(name, states_dict):
    print("Reading file " + name + "...")
    file_str = ""
    try:
        with open(name, "r") as f:
            file_str = f.read()
    except:
        try:
            with open(name, "r", encoding='utf-8') as f:
                file_str = f.read()
        except:
            try:
                with open(name, "r", encoding='utf-8-sig') as f:
                    file_str = f.read()
            except Exception as e:
                print("Could not read file " + name + "!")
                print(e)
    if not file_str.strip():
        return
    try:
        state_id = int(re.search(r"id\s*=\s*([0-9]+)", file_str, re.IGNORECASE).group(1))
        province_ids = [int(x) for x in re.search(r"(?:provinces\s*=\s*\{)((\s|.)*?)(?:\})", file_str, re.IGNORECASE).group(1).split()]
        manpower = int(re.search(r"(?:manpower\s*=\s*)([0-9]+)", file_str, re.IGNORECASE).group(1))
        try:
            owner = re.search(r"(?:owner\s*=\s*)(\"?[a-zA-Z]{3}\"?)", file_str, re.IGNORECASE).group(1)
        except:
            try:
                owner = re.search(r"(?:controller\s*=\s*)(\"?[a-zA-Z]{3}\"?)", file_str, re.IGNORECASE).group(1)
            except:
                owner = "---"
        try:
            category = re.search(r"(?:category\s*=\s*)(\"?[a-zA-Z_]+\"?)", file_str, re.IGNORECASE).group(1)
        except:
            category = "wasteland"
        industrial_complex = re.search(r"(?:industrial_complex\s*=\s*)([0-9]+)", file_str, re.IGNORECASE)
        if industrial_complex:
            industrial_complex = int(industrial_complex.group(1))
        else:
            industrial_complex = 0
        arms_factory = re.search(r"(?:arms_factory\s*=\s*)([0-9]+)", file_str, re.IGNORECASE)
        if arms_factory:
            arms_factory = int(arms_factory.group(1))
        else:
            arms_factory = 0
        infrastructure = re.search(r"(?:infrastructure\s*=\s*)([0-9]+)", file_str, re.IGNORECASE)
        if infrastructure:
            infrastructure = int(infrastructure.group(1))
        else:
            infrastructure = 0
        dockyard = re.search(r"(?:dockyard\s*=\s*)([0-9]+)", file_str, re.IGNORECASE)
        if dockyard:
            dockyard = int(dockyard.group(1))
        else:
            dockyard = 0
        states_dict[state_id] = State(state_id, province_ids, manpower, owner, category, industrial_complex, arms_factory, infrastructure, dockyard)
    except:
        print("File %s failed to load!" % name)
        print(file_str)
        traceback.print_exc()

def load_pdx_colors_file(name):
    print("Reading file " + name + "...")
    try:
        with open(name, "r") as f:
            file_str = f.read()
    except:
        try:
            with open(name, "r", encoding='utf-8') as f:
                file_str = f.read()
        except:
            try:
                with open(name, "r", encoding='utf-8-sig') as f:
                    file_str = f.read()
            except:
                print("Could not read file " + name + "!")
    file_str = re.sub(r"#.*$", "", file_str, re.MULTILINE)
    pdx_colors = re.findall(r"([A-Z]{3})\s*=\s*{\s*color\s*=\s*rgb\s*{([\s0-9]*)\s*}", file_str, re.IGNORECASE)
    pdx_colors_hsv = re.findall(r"([A-Z]{3})\s*=\s*{\s*color\s*=\s*hsv\s*{([\s0-9\.]*)\s*}", file_str, re.IGNORECASE)
    colors = {}
    for color in pdx_colors:
        colors[color[0]] = [int(x) for x in color[1].split()]
    for color in pdx_colors_hsv:
        hsv = color[1].split()
        colors[color[0]] = [round(255 * float(x)) for x in colorsys.hsv_to_rgb(float(hsv[0]), float(hsv[1]), float(hsv[2]))]
    return colors

def count_colors(states_dict, provinces_rev, provinces_image):
    pixels = provinces_image.load()
    totpix = 0
    statpix = 0
    for i in range(provinces_image.size[0]):
        for j in range(provinces_image.size[1]):
            if pixels[i,j] in provinces_rev:
                totpix += 1
                provid = provinces_rev[pixels[i, j]]
                if provid in providstate:
                    statpix += 1
                    providstate[provid].pixels += 1
    print(totpix, statpix)

def create_states_map(colors_replacement_dict, provinces_image, water_color):
    water_color = (water_color[0], water_color[1], water_color[2])
    pixels = provinces_image.load()
    print("Coloring pixels...")
    for i, j in tqdm(itertools.product(range(provinces_image.size[0]), range(provinces_image.size[1])), total=provinces_image.size[0]*provinces_image.size[1]):
        if pixels[i, j] in colors_replacement_dict:
            pixels[i, j] = colors_replacement_dict[pixels[i, j]][0]
        else:
            pixels[i, j] = water_color

def create_states_map_with_id(colors_replacement_dict, provinces_image, water_color, font_name):
    state_pixels = defaultdict(list)
    water_color = (water_color[0], water_color[1], water_color[2])
    pixels = provinces_image.load()
    print("Coloring pixels...")
    for i, j in tqdm(itertools.product(range(provinces_image.size[0]), range(provinces_image.size[1])), total=provinces_image.size[0]*provinces_image.size[1]):
        if pixels[i, j] in colors_replacement_dict:
            res = colors_replacement_dict[pixels[i, j]]
            pixels[i, j] = res[0]
            state_pixels[res[1]].append((i, j))
        else:
            pixels[i, j] = water_color
    
    draw = ImageDraw.Draw(provinces_image)
    try:
        font = ImageFont.truetype(font_name, 10)
    except:
        print("Font " + font_name + "not found, using system default. This probably won't look good.")
        font = ImageFont.load_default()
    size = provinces_image.size
    for key, value in state_pixels.items():
        state_pixels[key] = (value, font.getsize(str(key)))
    print("Generating ID positions...")
    kvps = list(state_pixels.items())
    positions = p_tqdm.p_map(find_id_position, kvps, [size]*len(kvps))
    for pos, state in positions:
        draw.text(pos, str(state), fill="black", font=font)

def find_id_position(kvp, size):
    # thanks to Martin Stancsics, https://stackoverflow.com/questions/37519238/python-find-center-of-object-in-an-image
    state = kvp[0]
    pixels = kvp[1][0]
    font_size = kvp[1][1]
    m = None
    X, Y = size
    m = np.zeros((X, Y))
    for pixel in pixels:
        m[pixel] = 1
    m = m / np.sum(np.sum(m))

    dx = np.sum(m, 1)
    dy = np.sum(m, 0)

    cx = np.sum(dx * np.arange(X))
    cy = np.sum(dy * np.arange(Y))

    return ((cx-font_size[0]/2,cy-font_size[1]/2), state)

def get_colors(name, states_dict):
    try:
        print("Reading file " + name + "...")
        with open(name, "rb") as handle:
            colors = pickle.load(handle)
    except:
        print("No file " + name + "found, creating new colors...")
        colors = [[(1/255)*BLUE_RBG[0], (1/255)*BLUE_RBG[1], (1/255)*BLUE_RBG[2]]]
    if len(states_dict) > len(colors)-1:
        for _ in tqdm(range(len(states_dict)-((len(colors)-1)))):
            colors.append(generate_new_color(colors))
        try:
            colors.remove([[(1/255)*BLUE_RBG[0], (1/255)*BLUE_RBG[1], (1/255)*BLUE_RBG[2]]])
        except:
            pass
        print("Saving file " + name + "...")
        try:
            with open(name, "wb") as handle:
                pickle.dump(colors, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except:
            print("Could not save file " + name + "! Continuing...")

    return colors

def get_sequential_colors(space, palette="Reds"):
    palette = sns.color_palette(palette, space)
    for idx, item in enumerate(palette):
        palette[idx] = [int(round(255 * x)) for x in item]
    return palette

def get_state_color(value, space, colors):
    for idx in range(0, len(colors)-1):
        if space[idx] <= value < space[idx+1]:
            return colors[idx]
    return colors[len(colors)-1]

def get_manpower_list(states_dict):
    manpower_list = []
    for state_id, state in states_dict.items():
        manpower_list.append(state.manpower/state.pixels)
    return sorted(manpower_list)

def get_total_factories_list(states_dict):
    total_factories_list = []
    for state_id, state in states_dict.items():
        total_factories_list.append(state.industrial_complex + state.arms_factory + state.dockyard)
    return sorted(total_factories_list)

def get_civ_factories_list(states_dict):
    civ_factories_list = []
    for state_id, state in states_dict.items():
        civ_factories_list.append(state.industrial_complex)
    return sorted(civ_factories_list)

def get_mil_factories_list(states_dict):
    mil_factories_list = []
    for state_id, state in states_dict.items():
        mil_factories_list.append(state.arms_factory)
    return sorted(mil_factories_list)

def get_infra_list(states_dict):
    infra_list = []
    for state_id, state in states_dict.items():
        infra_list.append(state.infrastructure)
    return sorted(infra_list)

def get_dockyards_list(states_dict):
    dockyards_list = []
    for state_id, state in states_dict.items():
        dockyards_list.append(state.dockyard)
    return sorted(dockyards_list)

def get_industry_per_capita(states_dict):
    ipc_states = set()
    for state_id, state in states_dict.items():
        ipc_states.add(round(state.industrial_complex+state.arms_factory+state.dockyard/state.manpower, 2))

    return sorted(list(ipc_states))

def get_industry_per_capita_per_tag(states_dict):
    ipc_dict = dict()
    ipc_states_dict = dict()
    for state_id, state in states_dict.items():
        if not state.owner in ipc_dict:
            ipc_dict[state.owner] = [state.industrial_complex+state.arms_factory+state.dockyard, state.manpower]
        else:
            ipc_dict[state.owner][0] = ipc_dict[state.owner][0] + state.industrial_complex+state.arms_factory+state.dockyard
            ipc_dict[state.owner][1] = ipc_dict[state.owner][1] + state.manpower
    
    for owner, values in ipc_dict.items():
        #ipc_dict[owner] = ipc_dict[owner][0]
        ipc_dict[owner] = ipc_dict[owner][0]/(ipc_dict[owner][1])
        ipc_dict[owner] = float("{:.1f}".format(ipc_dict[owner]))

    print(ipc_dict)

    for state_id, state in states_dict.items():
        ipc_states_dict[state_id] = ipc_dict[state.owner]

    return (ipc_states_dict, sorted(list({x for x in ipc_dict.values()})))
    
def get_manpower_per_factory_per_tag(states_dict):
    ipc_dict = dict()
    ipc_states_dict = dict()
    for state_id, state in states_dict.items():
        if not state.owner in ipc_dict:
            ipc_dict[state.owner] = [state.industrial_complex+state.arms_factory+state.dockyard, state.manpower]
        else:
            ipc_dict[state.owner][0] = ipc_dict[state.owner][0] + state.industrial_complex+state.arms_factory+state.dockyard
            ipc_dict[state.owner][1] = ipc_dict[state.owner][1] + state.manpower
    
    for owner, values in ipc_dict.items():
        ipc_dict[owner] = ipc_dict[owner][1]/(ipc_dict[owner][0])
        #ipc_dict[owner] = float("{:.2f}".format(ipc_dict[owner]))

    print(ipc_dict)

    for state_id, state in states_dict.items():
        ipc_states_dict[state_id] = ipc_dict[state.owner]

    return (ipc_states_dict, sorted(list({x for x in ipc_dict.values()})))

def generate_legend_and_colors(steps, data_list, title_str, mode, palette="Reds"):
    if mode == 1 or mode > 8:
        steps = np.linspace(0, 1, num=steps)
        space = np.quantile(data_list, steps)
        colors = get_sequential_colors(len(space), palette)
    elif mode == 8:
        space = data_list
        colors = get_sequential_colors(len(space), palette)
    else:
        space = np.linspace(0, data_list[-1], num=data_list[-1]+1, dtype=int)
        steps = data_list[-1]+1
        colors = get_sequential_colors(steps, palette)
    if mode == 1 or mode > 7:
        space[0] = 0
    labels = []
    if mode == 1 or mode > 8:
        for idx, label in enumerate(space):
            if idx < len(space)-1:
                labels.append("%.2f - %.2f" % (label, space[idx+1]))
            else:
                labels.append("%.2f+" % (label))
        le = len(space)-1
    else:
        labels = space
        le = len(space)
    fig = plt.figure()
    patches = [
        mpatches.Patch(color=color, label=label)
        for label, color in zip(labels, sns.color_palette(palette, le))]
    fig.legend(patches, labels, loc='center', title=title_str, frameon=False)
    name = args.output.split(".", 2)
    fig.savefig('%s_legend.%s' % (name[0], name[1]), bbox_inches='tight')
    return (colors, space)

#############################

def main():
    water_color = [(1/255)*BLUE_RBG[0], (1/255)*BLUE_RBG[1], (1/255)*BLUE_RBG[2]]

    #print(sns.color_palette("Blues"))

    #load_pdx_colors_file("colors.txt")

    mode = int(args.mode)
    if mode < 0 or mode > 10:
        sys.exit("Wrong mode - must be between 0 and 9")

    try:
        dir = readable_dir(args.states)
    except:
        sys.exit("states is not a vaild folder.")

    states_path = args.states
    states_dict = {}
    for file in os.listdir(states_path):
        if file.endswith(".txt"):
            load_state_file(os.path.join(states_path, file), states_dict)

    provinces = load_definition(args.definition)
    provinces_rev = provinces[1]
    provinces = provinces[0]
    province_map = load_provinces(args.provinces)
    count_colors(states_dict, provinces_rev, province_map)

    if mode == 1:
        print("Mode %d - Population per pixel" % mode)
        manpower_list = get_manpower_list(states_dict)
        lc = generate_legend_and_colors(MANPOWER_STEPS, manpower_list, "Population per pixel/7.114km^2", mode)
        colors = lc[0]
        space = lc[1]
    elif mode == 2:
        print("Mode %d - Political" % mode)
        colors = load_pdx_colors_file(args.colors)
    elif mode == 3:
        print("Mode %d - Total Factories" % mode)
        factories_list = get_total_factories_list(states_dict)
        factories_steps = factories_list[-1]
        lc = generate_legend_and_colors(factories_steps, factories_list, "Total Factories in State", mode)
        colors = lc[0]
        space = lc[1]
    elif mode == 4:
        print("Mode %d - Civilian Factories" % mode)
        factories_list = get_civ_factories_list(states_dict)
        factories_steps = factories_list[-1]
        lc = generate_legend_and_colors(factories_steps, factories_list, "Civilian Factories in State", mode, "Oranges")
        colors = lc[0]
        space = lc[1]
    elif mode == 5:
        print("Mode %d - Military Factories" % mode)
        factories_list = get_mil_factories_list(states_dict)
        factories_steps = factories_list[-1]
        lc = generate_legend_and_colors(factories_steps, factories_list, "Military Factories in State", mode, "Greens")
        colors = lc[0]
        space = lc[1]
    elif mode == 6:
        print("Mode %d - Infrastructure" % mode)
        factories_list = get_infra_list(states_dict)
        factories_steps = factories_list[-1]
        lc = generate_legend_and_colors(factories_steps, factories_list, "Infrastructure in State", mode, "Oranges")
        colors = lc[0]
        space = lc[1]
    elif mode == 7:
        print("Mode %d - Dockyards" % mode)
        factories_list = get_dockyards_list(states_dict)
        factories_steps = factories_list[-1]
        lc = generate_legend_and_colors(factories_steps, factories_list, "Dockyards in State", mode, "Blues")
        colors = lc[0]
        space = lc[1]
    elif mode == 8:
        print("Mode %d - Industry per capita" % mode)
        ipc_dict = get_industry_per_capita_per_tag(states_dict)
        ipc_values = ipc_dict[1]
        print(ipc_values)
        ipc_dict = ipc_dict[0]
        ipc_steps = len(ipc_values)
        lc = generate_legend_and_colors(ipc_steps, ipc_values, "Factories per 1mil pop", mode, "Oranges")
        colors = lc[0]
        space = lc[1]
    elif mode == 9:
        print("Mode %d - Industry per capita state" % mode)
        ipc_list = get_industry_per_capita(states_dict)
        lc = generate_legend_and_colors(13, ipc_list, "Factories per pop", mode)
        colors = lc[0]
        space = lc[1]
    elif mode == 10:
        print("Mode %d - Manpower per factory" % mode)
        ipc_dict = get_manpower_per_factory_per_tag(states_dict)
        ipc_values = ipc_dict[1]
        print(ipc_values)
        ipc_dict = ipc_dict[0]
        lc = generate_legend_and_colors(12, ipc_values, "Manpower per factory", mode, "Oranges")
        colors = lc[0]
        space = lc[1]
    else:
        print("Mode %d - States" % mode)
        colors = get_colors(args.colors, states_dict)

    colors_replacement_dict = {}

    print("Determining state colors...")
    for state_id, state in tqdm(states_dict.items()):
        if mode == 1:
            color = get_state_color(state.manpower/state.pixels, space, colors)
        elif mode == 2:
            try:
                color = colors[state.owner]
            except:
                print("%s not in colors" % state.owner)
        elif mode == 3:
            color = get_state_color(state.industrial_complex+state.arms_factory+state.dockyard, space, colors)
        elif mode == 4:
            color = get_state_color(state.industrial_complex, space, colors)
        elif mode == 5:
            color = get_state_color(state.arms_factory, space, colors)
        elif mode == 6:
            color = get_state_color(state.infrastructure, space, colors)
        elif mode == 7:
            color = get_state_color(state.dockyard, space, colors)
        elif mode == 8 or mode == 10:
            color = get_state_color(ipc_dict[state_id], space, colors)
        elif mode == 9:
            color = get_state_color(state.industrial_complex+state.arms_factory+state.dockyard/state.manpower, space, colors)
        else:
            color = [round(255 * x) for x in colors.pop()]

        #print("STATE %s: COLOR: %s" % (str(state_id), color))
        for province in state.provinces:
            if province in provinces:
                colors_replacement_dict[provinces[province]] = ((color[0], color[1], color[2]), state_id)

    print("Generating map image...")
    if args.no_ids:
        create_states_map(colors_replacement_dict, province_map, [round(255 * x) for x in water_color])
    else:
        create_states_map_with_id(colors_replacement_dict, province_map, [round(255 * x) for x in water_color], args.font)

    province_map.show()
    print("Saving file " + args.output + "...")
    province_map.save(args.output, "PNG")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Given valid provinces.bmp, definition.csv files and a folder of state history files (or strategic region files), generate an image containing a map of states with their IDs.')
    parser.add_argument( 'mode',
                        help='Mode: 0 - states, 1 - population per pixel, 2 - political, 3 - total factories, 4 - civ factories, 5 - mil factories, 6 - infra, 7 - nav factories, 8 - industry per capita')
    parser.add_argument('provinces',
                        help='Path to provinces.bmp file')
    parser.add_argument( 'definition',
                        help='Path to definition.csv file')
    parser.add_argument( 'states',
                        help='Path to \'history/states\' or \'map/strategicregions\' folder')
    parser.add_argument( 'output',
                        help='Name of output file')
    parser.add_argument('-c', '--colors', required=False, default="hoi4statemapgenerator_colors.pickle",
                        help='Name of pregenerated colors.pickle file (Default: hoi4statemapgenerator_colors.pickle)')
    parser.add_argument('-f', '--font', required=False, default="ARIALN.TTF",
                        help='Name of font to use (Default: ARIALN.TTF)')
    parser.add_argument( '-nid', '--no_ids', action='store_true', required=False, default=False,
                        help='Do not put IDs on the map (Default: False)')
    args = parser.parse_args()
    main()
