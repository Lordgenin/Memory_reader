import sys
import memory_reader

def main(target_pid, output_format, output_file):
    # Get a list of memory regions from the target process
    memory_regions = memory_reader.list_memory_regions(target_pid)

    # Filter memory regions based on specific criteria, if needed
    # For example, you could filter regions with specific protection flags

    # Read the memory data for each region and convert it to the desired output format
    memory_data_list = []
    for region in memory_regions:
        memory_data = memory_reader.read_memory_region(target_pid, region)
        formatted_data = memory_reader.memory_data_to_json(memory_data, region.base_address)
        memory_data_list.append(formatted_data)

    # Save the memory data to the specified output file
    memory_reader.save_memory_data_to_file(memory_data_list, output_format, output_file)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: main.py <target_pid> <output_format> <output_file>")
        sys.exit(1)

    pid = int(sys.argv[1])
    format = sys.argv[2]
    file = sys.argv[3]
    main(pid, format, file)
