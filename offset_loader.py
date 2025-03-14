def load_offsets(filename="offsets.txt"):
    offsets = {}
    with open(filename, "r") as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split("=")
                offsets[key.strip()] = int(value.strip(), 16)
    return offsets
