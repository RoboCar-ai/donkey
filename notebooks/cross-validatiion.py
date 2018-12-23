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
            d_coords = []

            batch_indices = indices[offset:offset+BATCH_SIZE]
            for i in batch_indices:
                data_path = data_paths[i]
                data = data_items[i]

                base_path = dirname(data_path)
                img = Image.open(join(base_path, data['cam/image_array']))
                X.append(np.array(img))

                # angles.append(data['user/angle'])
                # throttles.append(data['user/throttle'])
                d_coords.append(data['user/d_coord'])

            yield np.array(X), [np.array(d_coords)]


k_fold = KFold(n_splits=N_FOLDS, shuffle=True)

dataset_names = [
    # '../d2/data/generated_road/surface_2',
    # '../d2/data/generated_road/surface_3'
    '../d2/data/default_track_sim'
]

data_paths = []

for dataset_name in dataset_names:
    data_paths += glob(join(dataset_name, '**', 'record*.json'))

print('Total samples: {}'.format(len(data_paths)))

data_items = []
for data_path in data_paths:
    with open(data_path, 'r') as f:
        data = json.loads(f.read())
        data_items.append(data)
val_losses = []

folds = k_fold.split(data_paths)

models_to_test = [
    models.KerasAppInceptionV3Loc1024,
    models.KerasAppInceptionV3Loc512,
    models.KerasAppInceptionV3Loc256
]


for model_to_test in models_to_test:
    for i, fold in enumerate(folds):
        train_indices, val_indices = fold

        train_gen = gen(train_indices)
        val_gen = gen(val_indices)

        train_steps = len(train_indices) // BATCH_SIZE
        val_steps = len(val_indices) // BATCH_SIZE

        model = model_to_test()

        base_path = '../d2/models/{}-cross-val-fold-{}'.format(model.__class__.__name__, i)

        history = model.train(train_gen=train_gen,
                              steps=train_steps,
                              val_steps=val_steps,
                              val_gen=val_gen,
                              saved_model_path=base_path + '.h5')

        with open(base_path + '.json'.format(i), 'w') as f:
            f.write(json.dumps(history.history))

        val_losses.append(min(history.history['val_loss']))

        K.clear_session()
        del model

print(val_losses)


# k_fold.split()




