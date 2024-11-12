import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def isoforest(data):
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].apply(lambda x: x.timestamp())

    label_encoders = {}
    for column in ['host', 'process', 'event_type', 'severity', 'ips']:
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column])
        label_encoders[column] = le
        
    X = df[['timestamp', 'host', 'process', 'event_type', 'ips', 'severity']]  # Features

    model = IsolationForest(contamination=0.05, random_state=42)  # contamination is the expected anomaly rate
    model.fit(X)

    # Predict anomalies (1 = normal, -1 = anomaly)
    df['anomaly'] = model.predict(X)
    return df
