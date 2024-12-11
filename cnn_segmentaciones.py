# -*- coding: utf-8 -*-
"""CNN Segmentaciones.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Ny91VabD5bdeloNbq-HQeWD-6F_ock-P
"""

# Importar bibliotecas necesarias
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
import tensorflow as tf
from tensorflow.keras import models, layers
from google.colab import drive
drive.mount('/content/drive')

import zipfile
from google.colab import drive

# Mount Google Drive (if not already mounted)
drive.mount('/content/drive')

# Fix the path to the zip file - Remove the extra //content
zip_path = '/content/drive/MyDrive/Colab Notebooks/descargas_kaggle/Segmentaciones.zip'
extract_path = '/content/dataset'  # Carpeta de destino

# Extraer
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Comprobar contenido
import os
os.listdir(extract_path)

# Comprobar el contenido de la carpeta "dataset"
dataset_contents = os.listdir("/content/dataset")
print(f"Contents of /content/dataset: {dataset_contents}")

# Comprobar el contenido de "Segmentaciones"
segmentaciones_contents = os.listdir("/content/dataset/Segmentaciones")
print(f"Contents of /content/dataset/Segmentaciones: {segmentaciones_contents}")

# Preparación de datos
data_dir = "/content/dataset/Segmentaciones/a. Training Set"
sub_folders = os.listdir(data_dir)

images = []
labels = []

# Cargar y preprocesar imágenes
for sub_folder in sub_folders:
    label = sub_folder
    path = os.path.join(data_dir, sub_folder)
    sub_folder_images = os.listdir(path)

    for image_name in sub_folder_images:
        image_path = os.path.join(path, image_name)

        # Cargar la imagen
        img = cv2.imread(image_path)

        # Convertir a escala de grises y redimensionar
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized_img = cv2.resize(gray_img, (256, 256))

        # Agregar las imágenes y etiquetas
        images.append(resized_img)
        labels.append(label)

# Convertir a arrays de numpy
images = np.array(images).reshape(-1, 256, 256, 1)  # Añadir canal para imágenes en escala de grises
labels = np.array(labels)

# Normalizar las imágenes (escala de 0 a 1)
images = images / 255.0

# Dividir en conjunto de entrenamiento y prueba
train_images, test_images, train_labels, test_labels = train_test_split(images, labels, test_size=0.2, random_state=42)

# Codificar las etiquetas
label_encoder = LabelEncoder()
train_labels_encoded = label_encoder.fit_transform(train_labels)
test_labels_encoded = label_encoder.transform(test_labels)

# Convertir etiquetas a formato one-hot si es necesario
train_labels_one_hot = to_categorical(train_labels_encoded)
test_labels_one_hot = to_categorical(test_labels_encoded)

# Construcción del modelo CNN
model = models.Sequential()

# Primera capa convolucional
model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 1)))
model.add(layers.MaxPooling2D((2, 2)))

# Segunda capa convolucional
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))

# Tercera capa convolucional
model.add(layers.Conv2D(128, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))

# Aplanamiento y capas densas
model.add(layers.Flatten())
model.add(layers.Dense(128, activation='relu'))
model.add(layers.Dropout(0.5))  # Regularización
model.add(layers.Dense(len(np.unique(labels)), activation='softmax'))  # Salida con tantas clases como etiquetas únicas

# Compilación del modelo
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Entrenamiento del modelo
history = model.fit(train_images, train_labels_encoded, epochs=15, batch_size=32,
                    validation_data=(test_images, test_labels_encoded))

# Evaluación del modelo
test_loss, test_acc = model.evaluate(test_images, test_labels_encoded, verbose=2)
print(f"Precisión en el conjunto de prueba: {test_acc:.2f}")

# Graficar precisión y pérdida
plt.plot(history.history['accuracy'], label='Precisión en entrenamiento')
plt.plot(history.history['val_accuracy'], label='Precisión en validación')
plt.xlabel('Épocas')
plt.ylabel('Precisión')
plt.legend()
plt.show()

plt.plot(history.history['loss'], label='Pérdida en entrenamiento')
plt.plot(history.history['val_loss'], label='Pérdida en validación')
plt.xlabel('Épocas')
plt.ylabel('Pérdida')
plt.legend()
plt.show()

# Predicciones con el modelo entrenado
predictions = model.predict(test_images)

# Visualización de predicciones
indices = [0, 10, 20, 30, 40]  # Cambiar índices para visualizar diferentes imágenes
plt.figure(figsize=(12, 8))
for i, idx in enumerate(indices):
    plt.subplot(1, len(indices), i + 1)
    plt.imshow(test_images[idx].reshape(256, 256), cmap='gray')
    plt.title(f"Pred: {np.argmax(predictions[idx])}\nReal: {test_labels_encoded[idx]}")
    plt.axis('off')
plt.tight_layout()
plt.show()

# Diccionario para mapear índices a nombres de etiquetas
class_names = {
    0: "1. Microaneurysms",
    1: "2. Hemorrhages",
    2: "3. Hard Exudates",
    3: "4. Soft Exudates",
    4: "5. Optical Disc",
    5: "6. Other Class 1",
    6: "7. Other Class 2",
    7: "8. Other Class 3",
    8: "9. Other Class 4",
    9: "10. Other Class 5"
}

# Predicciones con el modelo entrenado
predictions = model.predict(test_images)

# Imprimir predicciones con nombres de etiquetas
for i in range(10):  # Cambia el rango para mostrar más ejemplos si lo deseas
    predicted_label_index = np.argmax(predictions[i])  # Índice de la clase predicha
    predicted_label_name = class_names[predicted_label_index]  # Nombre de la clase predicha
    true_label_index = test_labels_encoded[i]  # Índice de la clase verdadera
    true_label_name = class_names[true_label_index]  # Nombre de la clase verdadera
    print(f"La red dice que la imagen es clase '{predicted_label_name}' y la clase verdadera es: '{true_label_name}'.")

# Ejemplo visualización para imágenes específicas
# Ensure indices are within the bounds of test_images and predictions
indices = [i for i in [1, 50, 8, 32, 29, 30, 100, 49] if i < len(test_images)]  # Filter out invalid indices
#indices = [1, 8, 32, 29, 30, 49]  # Example with valid indices

for idx in indices:
    predicted_label_index = np.argmax(predictions[idx])
    predicted_label_name = class_names[predicted_label_index]
    true_label_index = test_labels_encoded[idx]
    true_label_name = class_names[true_label_index]
    print(f"Imagen {idx}: Predicción -> {predicted_label_name}, Etiqueta real -> {true_label_name}")