import re
from datetime import datetime

class Dataset:
    def __init__(self, name, unit="", data=None):
        self.name = name      # e.g., "Voltage"
        self.data = data      # list of values, e.g., [46.8, 47.1, ...]
        self.unit = unit      # e.g., "V"

    def __repr__(self):
        return f"Data(name='{self.name}', unit='{self.unit}', data_length={len(self.data)})"
    
    def add_datum(self, x, y):
        self.data.append([x, y])

def parse_file(file):
    all_datasets = []
    errors = []

    re_type = r"\[\d+:\d+:\d+]\s+(ERR|DAT)\s+.*"
    re_err = r"\[(.*?)\]\s+ERR\s+(.*)"
    re_dat = r"\[(.*?)\]\s+\w+\s+([A-Za-z ]+):\s*([\d.]+)(\D+)"

    for line in file:
        type_match = re.search(re_type, line)

        if type_match is None: return

        if type_match.group(1) == "DAT":
            time, name, value, unit = re.match(re_dat, line).groups()
            time, value = datetime.strptime(time, "%H:%M:%S"), float(value)
            dataset = next((d for d in all_datasets if d.name == name), None)

            if dataset is not None:
                dataset.add_datum(time, value)
            else:
                all_datasets.append(Dataset(name, unit, [[time, value]]))  
        else:
            time, message = re.match(re_err, line).groups()
            errors.append([datetime.strptime(time, "%H:%M:%S"), message])

    return all_datasets, errors

def parse_filename(file_path):
    try:
        filename = file_path.split("/")[-1]
        timestamp = filename.split("_")[1][:4]  # MMDD
        month = timestamp[:2]
        day = timestamp[2:4]
        return f"Date: {month}/{day}"
    except:
        return filename.split("_")[-1]
        
