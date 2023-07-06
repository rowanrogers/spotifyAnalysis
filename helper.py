import json
import re
def write_output(json_object, output_file: str):

    if not bool(re.search("\.json", output_file)):
        raise Exception('Please ensure `output_file` is a `.json` file')

    # Writing to sample.json
    with open(output_file, "w") as outfile:
        json.dump(json_object.json(), outfile)

    print("Output written successfully")