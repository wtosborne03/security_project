import matplotlib.pyplot as plt
import plotly.express as px

def plot_logs(df):
    df['Timestamp'].value_counts().sort_index().plot(kind='line')
    plt.xlabel('Time')
    plt.ylabel('Number of Events')
    plt.title('Log Events Over Time')
    plt.show()

def plot_sources(df):
    df['Source'].value_counts().plot(kind='bar')
    plt.xlabel('Source')
    plt.ylabel('Number of Events')
    plt.title('Log Events by Source')
    plt.show()

def interactive_plot(df):
    fig = px.line(df['Timestamp'].value_counts().sort_index(), title='Log Events Over Time')
    fig.show()