from glob import glob
import json

data_paths = glob('../d2/data/default_track_sim/**/record*.json')

for data_path in data_paths:
    d = None
    if data_path.startswith('../d2/data/default_track_sim/center_lane'):
        d = 0.
    elif data_path.startswith('../d2/data/default_track_sim/left_lane'):
        d = -1.
    elif data_path.startswith('../d2/data/default_track_sim/right_lane'):
        d = 1.
    else:
        raise ValueError('no valid d_coord')

    with open(data_path, 'r') as f:
        data = json.loads(f.read())

    data['user/d_coord'] = d

    with open(data_path, 'w') as f:
        f.write(json.dumps(data))
