class Dataset:
    def __init__(self, name, unit="", data=[]):
        self.name = name      # e.g., "Voltage"
        self.data = data      # list of values, e.g., [46.8, 47.1, ...]
        self.unit = unit      # e.g., "V"

    def __repr__(self):
        return f"Data(name='{self.name}', unit='{self.unit}', data_length={len(self.data)})"


def parse_file(file):
    return
