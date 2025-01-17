import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf

f = "E://项目//ML//LR//jena_climate_2009_2016.csv"



df = pd.read_csv(f)


print(df.shape[0]/6/24)

# 气温，大气压力和空气密度
features_considered = ['p (mbar)', 'T (degC)', 'rho (g/m**3)']

features = df[features_considered]
features.index = df['Date Time']


# 数据标准化
TRAIN_SPLIT = 300000
dataset = features.values
data_mean = dataset[:TRAIN_SPLIT].mean(axis=0)
data_std = dataset[:TRAIN_SPLIT].std(axis=0)
dataset = (dataset-data_mean)/data_std





def multivariate_data(dataset, target, start_index, end_index, history_size,
                      target_size, step, single_step=False):
    data = []
    labels = []

    start_index = start_index + history_size

    if end_index is None:
        end_index = len(dataset) - target_size

    for i in range(start_index, end_index):
        indices = range(i-history_size, i, step) # step表示间隔采样步长，6表示每个小时只使用一个采样值（原数据集每10分钟采集一次）
        data.append(dataset[indices])

        if single_step:
            print(i+target_size)

            labels.append(target[i+target_size])
        else:
            labels.append(target[i:i+target_size])

    return np.array(data), np.array(labels)


past_history = 720
future_target = 72
STEP = 6

print(dataset[:8])

x_train_single, y_train_single = multivariate_data(dataset, dataset[:, 1], 0,
                                                   TRAIN_SPLIT, past_history,
                                                   future_target, STEP,
                                                   single_step=True)

x_val_single, y_val_single = multivariate_data(dataset, dataset[:, 1], TRAIN_SPLIT, 
                                               None, past_history,
                                               future_target, STEP,
                                               single_step=True)


train_data_single = tf.data.Dataset.from_tensor_slices((x_train_single, y_train_single))

BUFFER_SIZE = 10000
BATCH_SIZE = 256
train_data_single = train_data_single.cache().shuffle(BUFFER_SIZE).batch(BATCH_SIZE).repeat()

val_data_single = tf.data.Dataset.from_tensor_slices((x_val_single, y_val_single))
val_data_single = val_data_single.batch(BATCH_SIZE).repeat()

print(x_train_single.shape)
print(x_train_single.shape[-2:])
print(y_train_single.shape)

# for x, y in val_data_single.take(1):
#     print(y[0].numpy())



single_step_model = tf.keras.models.Sequential()
single_step_model.add(tf.keras.layers.LSTM(32, input_shape=x_train_single.shape[-2:]))
single_step_model.add(tf.keras.layers.Dense(1))


# for x, y in train_data_single.take(1):
#     print(x.shape)   # (256, 120, 3)
#     print(y.shape)   # (256,)
#     print('Output shape:', single_step_model(x).shape  )   # Output shape: (256, 1)


single_step_model.compile(optimizer=tf.keras.optimizers.RMSprop(), loss='mae')
single_step_history = single_step_model.fit(train_data_single, epochs=10,
                                                steps_per_epoch=200,
                                                validation_data=val_data_single,
                                                validation_steps=50)


for x, y in val_data_single.take(3):
    print(x.shape)
    print(y.shape)
    print(single_step_model.predict(x).shape)
#         plot = show_plot([x[0][:, 1].numpy(), y[0].numpy(),
#                         single_step_model.predict(x)[0]], 12,
#                        'Single Step Prediction')
#         plot.show()