#Read JSON files from a folder and merge them into one JSON file
import json
import os
def merge_json_files(folder_path, output_file):
    #find all decisions.json files in the folder or its subfolders and read them
    #json format {"onto":[]} + {"onto2":[]} -> {"onto":[], "onto2":[]}
    merged_result = {}
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
               if 'decisons.json' in filename:
                print('Found file: ', os.path.join(root, filename))
                with open(os.path.join(root, filename), 'r') as f:
                    data = json.load(f)
                    merged_result.update(data)
    
    with open(os.path.join(folder_path, output_file), 'w') as f:
        json.dump(merged_result, f, indent=4)

merge_json_files('../Logs_Multiple_Defects(VM3)', 'merged_decisions_normalized_VM3.json')

