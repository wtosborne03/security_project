import re
import pandas as pd

def parse_log(log_file):
    with open(log_file, 'r') as file:
        logs = file.readlines()
    parsed_logs = []
    for log in logs:
        match = re.match(r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(.*)', log)
        if match:
            parsed_logs.append(match.groups())
    return pd.DataFrame(parsed_logs, columns=['Timestamp', 'Source', 'Message'])

def clean_data(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df.dropna(subset=['Timestamp'], inplace=True)  # Drop rows with invalid timestamps
    return df