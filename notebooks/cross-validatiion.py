from sklearn.model_selection import KFold
from glob import glob
from os.path import join, dirname
import json
import numpy as np
import donkeycar.parts.keras as models
from PIL import Image
import keras.backend as K

BATCH_SIZE = 128
N_FOLDS = 5


def gen(indices):
    num_of_samples = len(indices)
    while True:
        for offset in range(0, num_of_samples, BATCH_SIZE):
            X = []
            angles = []
            throttles = []

            batch_indices = indices[offset:offset+BATCH_SIZE]
            for i in batch_indices:
                data_path = data_paths[i]
                data = data_items[i]

                base_path = dirname(data_path)
                img = Image.open(join(base_path, data['cam/image_array']))
                X.append(np.array(img))

                angles.append(data['user/angle'])
                throttles.append(data['user/throttle'])

            yield np.array(X), [np.array(angles), np.array(throttles)]


k_fold = KFold(n_splits=N_FOLDS, shuffle=True)

dataset_names = [
    # '../d2/data/generated_road/surface_2',
    # '../d2/data/generated_road/surface_3'
    '/home/blown302/donkey/d2/data/default_track_sim'
]

data_paths = []
imgs = []

for dataset_name in dataset_names:
    data_paths += glob(join(dataset_name, '**', 'record*.json'))

data_items = []
for data_path in data_paths:
    with open(data_path, 'r') as f:
        data = json.loads(f.read())
        data_items.append(data)
val_losses = []

for i, fold in enumerate(k_fold.split(data_paths)):
    train_indices, val_indices = fold

    train_gen = gen(train_indices)
    val_gen = gen(val_indices)

    train_steps = len(train_indices) // BATCH_SIZE
    val_steps = len(val_indices) // BATCH_SIZE

    model = models.KerasLinear()

    history = model.train(train_gen=train_gen, steps=train_steps, val_steps=val_steps, val_gen=val_gen, saved_model_path='../d2/models/linear-cross-val-fold-{}.h5'.format(i))

    with open('../d2/models/linear-cross-val-fold-history-{}.json'.format(i), 'w') as f:
        f.write(json.dumps(history.history))

    val_losses.append(min(history.history['val_loss']))

    K.clear_session()
    del model

print(val_losses)


# k_fold.split()




