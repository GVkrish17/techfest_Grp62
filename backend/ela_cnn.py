import os
import numpy as np
import cv2
from PIL import Image, ImageChops, ImageEnhance
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

def convert_to_ela_image(image_path, quality=90):
    original = Image.open(image_path).convert('RGB')
    
    # Save as JPEG at 90% quality
    resaved_path = 'temp_ela.jpg'
    original.save(resaved_path, 'JPEG', quality=quality)
    
    resaved = Image.open(resaved_path)
    ela_image = ImageChops.difference(original, resaved)
    
    # Enhance the difference
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff
    
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
    
    return ela_image

def load_dataset():
    data = []
    labels = []
    
    for label, folder in enumerate(["real", "fake"]):
        path = os.path.join('dataset', folder)
        for file in os.listdir(path):
            try:
                full_path = os.path.join(path, file)
                ela_image = convert_to_ela_image(full_path).resize((128, 128))
                data.append(np.array(ela_image) / 255.0)  # Normalize values to 0-1
                labels.append(label)
            except Exception as e:
                print(f"Error loading image {file}: {e}")
    
    data = np.array(data)
    labels = to_categorical(labels, num_classes=2)  # 2 classes: real and fake
    
    return data, labels

def build_model():
    model = Sequential()

    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)))
    model.add(MaxPooling2D((2, 2)))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(2, activation='softmax'))

    model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])
    
    return model

def train():
    data, labels = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2)
    
    model = build_model()
    
    history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=10, batch_size=16)
    
    # Save model
    model.save('model/ela_cnn.h5')
    
    # Plot accuracy and loss
    plt.plot(history.history['accuracy'], label='train_accuracy')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
    plt.legend()
    plt.title('Model Accuracy')
    plt.show()

if __name__ == "__main__":
    train()
