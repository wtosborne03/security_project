from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

def kmeans_clustering(df):
    kmeans = KMeans(n_clusters=3)
    df['Cluster'] = kmeans.fit_predict(df[['Timestamp', 'Source']])
    return df

def isolation_forest(df):
    model = IsolationForest(contamination=0.01)
    df['Anomaly'] = model.fit_predict(df[['Timestamp', 'Source']])
    return df

def alert(df):
    anomalies = df[df['Anomaly'] == -1]
    if not anomalies.empty:
        print('ALERT: Suspicious activity detected!')