import json
import glob
import random

for file_path in glob.glob('content/activities/*.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    activities = data.get('activities', [])
    modified = False
    
    for activity in activities:
        options = activity.get('options')
        if options and len(options) > 0:
            original = list(options)
            random.shuffle(options)
            if options != original:
                modified = True
                
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f'Shuffled options in {file_path}')
print('Done shuffling.')
