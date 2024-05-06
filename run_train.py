# -*- coding: utf-8 -*-
"""Untitled5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DWFpw24kTzc6mpH0001QqYooGA09J-3U
"""

import os
import json
import csv
import pandas as pd


def process_data(input_csv, json_directory, output_csv):
    json_files = {}

    for root, _, files in os.walk(json_directory):
        for _file in files:
            if _file.endswith(".json"):
                _file_name = os.path.splitext(_file)[0]
                json_files[_file_name] = os.path.join(root, _file)

    with open(input_csv) as f_in, open(output_csv, 'w') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        next(reader)

        # Add labels to the header
        labels = ['pair_id', 'text1', 'text2', 'Geography', 'Entities', 'Time', 'Narrative', 'Overall', 'Style', 'Tone']
        writer.writerow(labels)

        for row in reader:
            id1, id2 = row[2].split("_")
            text_1 = text_2 = None

            if id1 in json_files:
                with open(json_files[id1]) as f1:
                    data1 = json.load(f1)
                    text_1 = [data1['title'] + '  [SEP]  ' + data1['text']]

            if id2 in json_files:
                with open(json_files[id2]) as f2:
                    data2 = json.load(f2)
                    text_2 = [data2['title'] + '  [SEP]  ' + data2['text']]

            if text_1 and text_2:
                writer.writerow(row[:3] + text_1 + text_2 + row[7:])


process_data('/content/semeval-2022_task8_train-data_batch.csv', '/content/output_dir', 'train.csv')

train_data = pd.read_csv('/content/train.csv')
train_data = train_data.dropna(subset=['text1', 'text2']).astype({'text1': 'str', 'text2': 'str'})

train_data[0:1]

def save_model_summary_to_file(model, file_name):
    with open(file_name, 'w') as f:
        # Define a function to write the summary lines to the file
        def write_to_file(line):
            f.write(line + '\n')

        # Call the model.summary() method with the custom print function
        model.summary(print_fn=write_to_file)

import re


class Preprocessor:
    def __init__(self, punctuation=True, url=True, number=True):
        self.punctuation = punctuation
        self.url = url
        self.number = number

    def apply(self, sentence: str) -> str:
        sentence = sentence.lower()
        sentence = sentence.replace('<unk>', '')
        if self.url:
            sentence = Preprocessor.remove_url(sentence)
        if self.punctuation:
            sentence = Preprocessor.remove_punctuation(sentence)
        if self.number:
            sentence = Preprocessor.remove_number(sentence)
        sentence = re.sub(r'\s+', ' ', sentence)
        return sentence

    @staticmethod
    def remove_punctuation(sentence: str) -> str:
        sentence = re.sub(r'[^\w\s]', ' ', sentence)
        return sentence

    @staticmethod
    def remove_url(sentence: str) -> str:
        sentence = re.sub(r'(https|http)?://(\w|\.|/|\?|=|&|%)*\b', ' ', sentence)
        return sentence

    @staticmethod
    def remove_number(sentence: str) -> str:
        sentence = re.sub(r'\d+', ' ', sentence)
        return sentence

# Clean the text data
preprocessor = Preprocessor()
train_data['text1'] = train_data['text1'].apply(preprocessor.apply)
train_data['text2'] = train_data['text2'].apply(preprocessor.apply)

train_data['text1'][0:3]

import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from matplotlib import pyplot as plt
from sentence_transformers import SentenceTransformer

# Split the training data into training and validation sets
train_set, valid_set = train_test_split(train_data, test_size=0.2, random_state=42)

learning_rate = 0.01
hidden_units = 256
num_of_epochs = 100
size_of_batch = 32

# Load the SentenceTransformer model
encodding_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

print("model loded")

# Tokenize and encode the training set using the SentenceTransformer model
encoded_articles1_train = np.array(encodding_model.encode(train_set['text1'].tolist()))
encoded_articles2_train = np.array(encodding_model.encode(train_set['text2'].tolist()))

# Tokenize and encode the validation set using the SentenceTransformer model
encoded_articles1_valid = np.array(encodding_model.encode(valid_set['text1'].tolist()))
encoded_articles2_valid = np.array(encodding_model.encode(valid_set['text2'].tolist()))

print("encoding completed")

# Define the Siamese network architecture
hidden_units = 256
input1 = tf.keras.layers.Input(shape=(encodding_model.get_sentence_embedding_dimension(),))
input2 = tf.keras.layers.Input(shape=(encodding_model.get_sentence_embedding_dimension(),))

x1 = tf.keras.layers.Dense(hidden_units, activation='relu', kernel_regularizer='l2')(input1)
x2 = tf.keras.layers.Dense(hidden_units, activation='relu', kernel_regularizer='l2')(input2)

# Additional Layers
# x1 = tf.keras.layers.Dense(hidden_units, activation='relu', kernel_regularizer='l2')(input1)
# x1 = tf.keras.layers.BatchNormalization(momentum=0.99, epsilon=0.001)(x1)
# x1 = tf.keras.layers.Dropout(0.4)(x1)

# x2 = tf.keras.layers.Dense(hidden_units, activation='relu', kernel_regularizer='l2')(input2)
# x2 = tf.keras.layers.BatchNormalization(momentum=0.99, epsilon=0.001)(x2)
# x2 = tf.keras.layers.Dropout(0.4)(x2)

# x1 = tf.keras.layers.Dense(128, activation='relu', kernel_regularizer='l2')(x1)
# x1 = tf.keras.layers.BatchNormalization(momentum=0.99, epsilon=0.001)(x1)
# x1 = tf.keras.layers.Dropout(0.4)(x1)

# x2 = tf.keras.layers.Dense(128, activation='relu', kernel_regularizer='l2')(x2)
# x2 = tf.keras.layers.BatchNormalization(momentum=0.99, epsilon=0.001)(x2)
# x2 = tf.keras.layers.Dropout(0.4)(x2)

# x1 = tf.keras.layers.Dense(64, activation='relu', kernel_regularizer='l2')(x1)
# x1 = tf.keras.layers.BatchNormalization(momentum=0.99, epsilon=0.001)(x1)
# x1 = tf.keras.layers.Dropout(0.4)(x1)

# x2 = tf.keras.layers.Dense(64, activation='relu', kernel_regularizer='l2')(x2)
# x2 = tf.keras.layers.BatchNormalization(momentum=0.99, epsilon=0.001)(x2)
# x2 = tf.keras.layers.Dropout(0.4)(x2)

similarity_function = tf.keras.layers.Dot(axes=1, normalize=True)
x = similarity_function([x1, x2])

output = tf.keras.layers.Dense(1, activation='linear')(x)
model = tf.keras.models.Model(inputs=[input1, input2], outputs=output)

# Define the contrastive loss function
# def contrastive_loss(y_true, y_pred):
#     margin = 1
#     square_pred = tf.square(y_pred)
#     margin_square = tf.square(tf.maximum(margin - y_pred, 0))
#     return tf.reduce_mean(y_true * square_pred + (1 - y_true) * margin_square)

# Compile the model with adam optimizer and contrastive loss
# model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), loss=contrastive_loss)

# Compile the model with SGD optimier 
# model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=learning_rate, momentum=0.9), loss='mse')

# Compile the model with adam optimizer and contrastive loss
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), loss='mse')

print("Model compilation completed")

# Define the early stopping callback
# early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)

# Train the model on the training data
history = model.fit(
    [encoded_articles1_train, encoded_articles2_train], train_set['Overall'],
    epochs=num_of_epochs, batch_size=size_of_batch,
    validation_data=([encoded_articles1_valid, encoded_articles2_valid], valid_set['Overall'])
    # ,callbacks=[early_stop]
)

print("Training completed")

save_model_summary_to_file(model, 'network.txt')

model.save('/content/saved_model.h5')

plt.plot(np.array(history.history['loss']), label="train")
plt.plot(np.array(history.history['val_loss']), label="validation")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.title("Training with Epoch: 100, learning Rate:0.01, Adam optimizer")
plt.legend()
plt.show()

similarity_scores_train = model.predict([encoded_articles1_train, encoded_articles2_train])
similarity_scores_train = np.round(similarity_scores_train).clip(1, 4)
mae_train = mean_absolute_error(train_set['Overall'], similarity_scores_train)

# Predict the similarity scores for the validation data
similarity_scores_valid = model.predict([encoded_articles1_valid, encoded_articles2_valid])
similarity_scores_valid = np.round(similarity_scores_valid).clip(1, 4)
mae_valid = mean_absolute_error(valid_set['Overall'], similarity_scores_valid)

print("Training MAE:", mae_train)
print("Validation MAE:", mae_valid)