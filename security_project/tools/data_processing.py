import pandas as pd

# Severity levels and types of events can vary by system. You may want to adjust or expand these mappings.
SEVERITY_KEYWORDS = {
    "CRITICAL": ["failed", "unauthorized", "denied"],
    "WARNING": ["timeout", "disconnected", "invalid"],
    "INFO": ["accepted", "connected", "successful"]
}

EVENT_TYPES = {
    "login": ["login", "signin", "authentication"],
    "logout": ["logout", "signoff"],
    "access": ["access", "connect", "session"]
}

class DataProcessor:
    """Processes raw log data for analysis and visualization."""

    def __init__(self, log_data: pd.DataFrame):
        self.log_data = log_data.copy()
    
    def clean_data(self):
        """Clean and preprocess log data."""
        # Drop rows with missing timestamps or messages
        self.log_data.dropna(subset=["timestamp", "message"], inplace=True)
        
        # Ensure timestamp column is in datetime format
        self.log_data["timestamp"] = pd.to_datetime(self.log_data["timestamp"], errors='coerce')
        self.log_data.dropna(subset=["timestamp"], inplace=True)  # Drop rows with invalid timestamps

        # Standardize hostnames and process names to lowercase for consistency
        self.log_data["host"] = self.log_data["host"].str.lower()
        self.log_data["process"] = self.log_data["process"].str.lower()

        # Strip leading/trailing whitespace in all string columns
        for col in ["host", "process", "message"]:
            self.log_data[col] = self.log_data[col].str.strip()

        return self

    def categorize_severity(self):
        """Categorize log entries by severity."""
        def determine_severity(message):
            for severity, keywords in SEVERITY_KEYWORDS.items():
                if any(keyword in message.lower() for keyword in keywords):
                    return severity
            return "INFO"  # Default to INFO if no keywords matched
        
        self.log_data["severity"] = self.log_data["message"].apply(determine_severity)
        return self

    def categorize_event_type(self):
        """Categorize log entries by event type."""
        def determine_event_type(message):
            for event_type, keywords in EVENT_TYPES.items():
                if any(keyword in message.lower() for keyword in keywords):
                    return event_type
            return "other"  # Default to 'other' if no keywords matched

        self.log_data["event_type"] = self.log_data["message"].apply(determine_event_type)
        return self

    def filter_by_severity(self, severity_levels=None):
        """Filter log data by specified severity levels."""
        if severity_levels is None:
            severity_levels = ["CRITICAL", "WARNING", "INFO"]
        self.log_data = self.log_data[self.log_data["severity"].isin(severity_levels)]
        return self

    def filter_by_date_range(self, start_date=None, end_date=None):
        """Filter log data to only include entries within a specific date range."""
        if start_date:
            self.log_data = self.log_data[self.log_data["timestamp"] >= start_date]
        if end_date:
            self.log_data = self.log_data[self.log_data["timestamp"] <= end_date]
        return self

    def get_summary_stats(self):
        """Generate summary statistics for analysis."""
        stats = {
            "total_logs": len(self.log_data),
            "critical_logs": len(self.log_data[self.log_data["severity"] == "CRITICAL"]),
            "warning_logs": len(self.log_data[self.log_data["severity"] == "WARNING"]),
            "info_logs": len(self.log_data[self.log_data["severity"] == "INFO"]),
            "login_events": len(self.log_data[self.log_data["event_type"] == "login"]),
            "logout_events": len(self.log_data[self.log_data["event_type"] == "logout"]),
            "access_events": len(self.log_data[self.log_data["event_type"] == "access"])
        }
        return stats

    def get_processed_data(self):
        """Return the processed DataFrame."""
        return self.log_data

# Example usage
if __name__ == "__main__":
    # Assume we have a sample DataFrame `df` with log data loaded from `log_ingestion.py`
    # Columns: ["timestamp", "host", "process", "message"]

    sample_data = [
        {"timestamp": "2024-11-12 10:23:00", "host": "localhost", "process": "sshd", "message": "Failed password for invalid user root"},
        {"timestamp": "2024-11-12 10:24:00", "host": "localhost", "process": "sshd", "message": "Accepted password for user admin"},
        {"timestamp": "2024-11-12 10:25:00", "host": "localhost", "process": "kernel", "message": "Connection from 192.168.1.1 established"}
    ]
    df = pd.DataFrame(sample_data)

    processor = DataProcessor(df)
    processor.clean_data().categorize_severity().categorize_event_type()
    processor.filter_by_severity(["CRITICAL", "WARNING"]).filter_by_date_range("2024-11-12", "2024-11-12")

    # Get summary statistics for an overview
    stats = processor.get_summary_stats()
    print("Summary Statistics:", stats)

    # Access the cleaned, categorized data
    processed_data = processor.get_processed_data()
    print("Processed Data:\n", processed_data)
