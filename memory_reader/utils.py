import json

def memory_data_to_json(memory_data, base_address):
    return {
        "base_address": hex(base_address),
        "data": memory_data.hex()
    }

def save_memory_data_to_file(memory_data, output_format, output_file):
    if output_format == "json":
        with open(output_file, "w") as f:
            json.dump(memory_data, f, indent=2)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
