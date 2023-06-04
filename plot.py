import argparse
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys

def parse_cli_args():
    parser = argparse.ArgumentParser(description='plot collected data')
    parser.add_argument('file', type=str, help='Serial port which is opened.')

    return parser.parse_args(args=None if sys.argv[1:] else ["--help"])

def plot_data(file_name):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_name)

    # Extract the time and value columns from the DataFrame
    time_ns = df['Time']
    values = df['Value']

    # Convert time to milliseconds for better visualization
    time_ms = time_ns / 1e6

    # Create the plot
    plt.plot(time_ms, values)
    plt.xlabel('Time (ms)')
    plt.ylabel('Value')
    filename_without_extension = os.path.splitext(file_name)[0]
    plt.title(filename_without_extension)
    plt.grid(True)
    plt.show()

if __name__=="__main__":
    args = parse_cli_args()
    file_name = args.file
    plot_data(file_name)


