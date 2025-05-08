import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.utils import shuffle
import joblib

folder = 'gestures'
dataframes = []

for file in os.listdir(folder):
    if file.endswith('.csv'):
        df = pd.read_csv(os.path.join(folder, file), header=None)
        dataframes.append(df)

df_all = pd.concat(dataframes)
df_all = shuffle(df_all)

X = df_all.iloc[:, :-1].values
y = df_all.iloc[:, -1].values

le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, stratify=y_encoded)

model = SVC(kernel='rbf', probability=True)
model.fit(X_train, y_train)

# Validación cruzada
scores = cross_val_score(model, X, y_encoded, cv=5)
print(f"Precisión media (CV 5-fold): {scores.mean():.2f}")

# Guardar modelo y codificador
os.makedirs('model', exist_ok=True)
joblib.dump(model, 'model/gesture_svm.pkl')
joblib.dump(le, 'model/label_encoder.pkl')
print("Modelo y codificador guardados en la carpeta 'model'")
