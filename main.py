from tkinter import filedialog as fd
import pandas as pd


def openfile():
    """Uses a GUI to select a file then returns the content of this file as a list of strings"""
    filename = fd.askopenfilename(title="Select a file", filetypes=[("AMBP50 Files", "*.awp")])
    with open(filename) as f:
        send_to_main = f.readlines()
    return send_to_main


def parse_data(line_of_data, temp_array):
    """Parses all known ABPM50 data elements from string and places into a dictionary
    Single dictionary entry ,entry for single reading number, is passed back"""
    temp_array[line_of_data[0:3]] = {
        "Year": int(line_of_data[4:8], 16),
        "Month": int(line_of_data[8:10], 16),
        "Day": int(line_of_data[10:12], 16),
        "Hour": int(line_of_data[12:14], 16),
        "Minute": int(line_of_data[14:16], 16),
        "BP1 Sys": int(line_of_data[20:22], 16),
        "BP2 Dia": int(line_of_data[24:26], 16),
        "MAP": int(line_of_data[28:30], 16),
        "HR": int(line_of_data[32:34], 16),
    }
    return temp_array


def export_to_csv(data_to_go, meta_dat):
    """Exports data to an CSV file, uses meta data to generate filename"""
    df = pd.DataFrame(data_to_go).T
    df.to_csv(fd.askdirectory(title="Select Save Directory") + "/" + meta_dat["Name"] + meta_dat["ID"] + ".csv")


def read_file(file):
    """Takes a .awp file which has been parsed into lines of strings. Returns a complete dictionary containing all
    readings and a second dictionary containing meta data. """
    data_array = {}
    meta_data = {}
    for lines in file:
        if lines[0] == "C":  # ignore the C numbers, whatever the hell they are
            continue
        if lines[0:2] == "ID":  # add ID field to meta_data
            meta_data["ID"] = lines[3:-1]
            continue
        if lines[0:4] == "Name":  # add Name field to meta_data
            meta_data["Name"] = lines[5:-1]
            continue
        if lines[0:3] == "Age":  # ignore Age field
            continue
        if lines[1] == "=":  # select single digit data lines
            adj_line = "00" + lines
            data_array = parse_data(adj_line, data_array)
        if lines[2] == "=":  # select double digit lines
            adj_line = "0" + lines
            data_array = parse_data(adj_line, data_array)
        if lines[3] == "=":  # select triple digit lines
            data_array = parse_data(lines, data_array)
        else:
            continue
    return data_array, meta_data


def identify_version(file):
    """Function to identify whether .awp file is version 1 or 2"""
    version = 1
    for line in file:
        if "FileVersion_Main=2" in line:
            version = 2
    return version


data, meta = read_file(openfile())
export_to_csv(data, meta)
