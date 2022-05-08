from tkinter import filedialog as fd
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox

plt.close("all")


class Dataset:
    def __init__(self, data, meta_data):
        self.data = data
        self.meta_data = meta_data


global current_data


def open_file():
    """Uses a GUI to select a file then returns the content of this file as a list of strings"""
    filename = fd.askopenfilename(title="Select a file", filetypes=[("ABPM50 Files", "*.awp")])
    with open(filename) as f:
        send_to_main = f.readlines()
    return send_to_main


def parse_data(line_of_data, temp_array):
    """Parses all known ABPM50 data elements from string and adds into a single entry dictionary and passes this back"""
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


def export_to_csv(df, meta_dat):
    """Formats and exports data to a CSV file, using metadata to generate the filename. """
    df = df[['DateTime', 'BP1 Sys', 'BP2 Dia', 'MAP', 'HR']].copy()
    df["DateTime"] = df["DateTime"].dt.strftime('%d/%m/%y %H:%M')
    df.rename(columns={'BP1 Sys': 'Systolic', 'BP2 Dia': 'Diastolic'}, inplace=True)
    df.to_csv(fd.askdirectory(title="Select Save Directory") + "/" + meta_dat["Name"] + meta_dat["ID"] + ".csv")


def export_to_excel(df, meta_dat):
    """Opens a window to select a save directory. Takes a dataframe and saves it to the selected directory as
    output.xlsx """
    df = df[['DateTime', 'BP1 Sys', 'BP2 Dia', 'MAP', 'HR']].copy()
    df["DateTime"] = df["DateTime"].dt.strftime('%d/%m/%y %H:%M')
    df.rename(columns={'BP1 Sys': 'Systolic', 'BP2 Dia': 'Diastolic'}, inplace=True)
    df.to_excel(fd.askdirectory(title="Select Save Directory") + meta_dat["Name"] + meta_dat["ID"] + ".xlsx")
    tk.messagebox.showinfo('Save Complete', 'Output saved!')


# GUI read_file method
def read_file():
    """opens a .awp file. Returns dataset item containing all readings(df) and meta data(dictionary). """
    file = open_file()
    version = identify_version(file)
    data_array = {}
    meta_data = {}
    for lines in file:
        if lines[0] == "C":  # ignore the C numbers
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
    df = pd.DataFrame(data_array).T  # Creates dataframe from dictionary
    df["DateTime"] = pd.to_datetime(df[["Year", "Month", "Day", "Hour", "Minute"]])
    global current_data
    current_data = Dataset(df, meta_data)
    number_of_entries = df.shape[0]
    save_button["state"] = "enabled"
    current_state_label["text"] = "File loaded \n" + \
                                  str(number_of_entries) + \
                                  " events loaded.\n" + \
                                  "Note: filename will be " + current_data.meta_data["Name"] \
                                  + current_data.meta_data["ID"] + ".xlsx\n" + \
                                  "you will be able to select save location after clicking save"


# Original read_file method
# def read_file(file):
#     """Takes a .awp file which has been parsed into lines of strings. Returns a pandas dataframe containing all
#     readings and a dictionary containing meta data. """
#     data_array = {}
#     meta_data = {}
#     for lines in file:
#         if lines[0] == "C":  # ignore the C numbers
#             continue
#         if lines[0:2] == "ID":  # add ID field to meta_data
#             meta_data["ID"] = lines[3:-1]
#             continue
#         if lines[0:4] == "Name":  # add Name field to meta_data
#             meta_data["Name"] = lines[5:-1]
#             continue
#         if lines[0:3] == "Age":  # ignore Age field
#             continue
#         if lines[1] == "=":  # select single digit data lines
#             adj_line = "00" + lines
#             data_array = parse_data(adj_line, data_array)
#         if lines[2] == "=":  # select double digit lines
#             adj_line = "0" + lines
#             data_array = parse_data(adj_line, data_array)
#         if lines[3] == "=":  # select triple digit lines
#             data_array = parse_data(lines, data_array)
#         else:
#             continue
#     df = pd.DataFrame(data_array).T  # Creates dataframe from dictionary
#     df["DateTime"] = pd.to_datetime(df[["Year", "Month", "Day", "Hour", "Minute"]])
#     return df, meta_data


def identify_version(file):
    """Function to identify whether .awp file is version 1 or 2. Function not yet in use"""
    version = 1
    for line in file:
        if "FileVersion_Main=2" in line:
            version = 2
    return version


def graph_observations(dataframe, title):
    """Takes a dataset and creates a graph of BP and MAP over time"""
    x = dataframe.DateTime
    a1 = pd.Series(dataframe["BP1 Sys"])
    a2 = pd.Series(dataframe["BP2 Dia"])
    a3 = pd.Series(dataframe["MAP"])
    plt.title(title)
    plt.plot(x, a1, marker="^")
    plt.plot(x, a2, marker="v")
    plt.axhline(y=130)
    plt.axhline(y=60)
    plt.plot(x, a3, linestyle="dotted", color='green')
    plt.bar(x=x, height=a1 - a2, bottom=a2, width=0.005, alpha=.2)
    plt.fill_between(x, a1, a2, color='blue', alpha=.1)
    plt.gcf().autofmt_xdate()
    plt.show()


#   Work in progress - GUI structure
root = tk.Tk()
root.title("ABPM50ex")
root.geometry('600x400+50+50')

current_state_label = tk.Label(root, text="No file currently opened",
                               font='Calibri 15 bold')
current_state_label.pack(pady=20)
open_button = ttk.Button(
    root,
    text="Open File",
    command=read_file
)
open_button.pack(
    ipadx=5,
    ipady=5,
    expand=True
)

graph_button = ttk.Button(
    root,
    text="Graph Data",
    command=lambda: graph_observations(current_data.data, current_data.meta_data["Name"])
)
graph_button.pack(
    ipadx=5,
    ipady=5,
    expand=True
)
save_button = ttk.Button(
    root,
    text="Save to Excel",
    command=lambda: export_to_excel(current_data.data, current_data.meta_data)
)
save_button.pack(
    ipadx=5,
    ipady=5,
    expand=True
)
save_button["state"] = "disabled"
root.mainloop()

# Working main structure
# data, meta = read_file(open_file())
# graph_observations(data, meta["Name"])
# export_to_csv(data, meta)
