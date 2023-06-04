to display help:
`python main.py -h` or just `python main.py`

example usage:
1. collect data and store in trial.csv: `python main.py /dev/ttyUSB0 -b 1250000 -s trial`
2. visualize with: `python -m plot.py trial.csv`
