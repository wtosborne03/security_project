import pandas as pd
from datetime import datetime
import re

class LogIngestor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

    def ingest_logs(self):
        """
        Reads logs from the specified file, parses the entries, and returns a DataFrame.
        Assumes log entries follow a standard format, e.g., syslog format with timestamp,
        log level, and message.
        """
        # Define empty list to hold parsed log entries
        logs = []

        with open(self.file_path, "r") as file:
            for line in file:
                # Example log line parsing (modify based on your log format)
                parsed_entry = self.parse_log_line(line)
                if parsed_entry:
                    logs.append(parsed_entry)

        # Create DataFrame from the parsed log entries
        log_df = pd.DataFrame(logs)
        
        
        # Convert timestamp column to datetime
        log_df['timestamp'] = pd.to_datetime(log_df['timestamp'], errors='coerce')
        
        return log_df

    def parse_log_line(self, line):
        """
        Parses a single line of log entry.
        Expected format:
            "Nov 12 10:09:56 hostname process_name: message"
        Returns a dictionary with parsed fields.
        """
        try:
            # Split the log line into components
            parts = line.strip().split(" ", 5)

            # Parse the date and time
            month_day_str = f"{parts[0]} {parts[1]} {parts[2]}"
            timestamp = datetime.strptime(month_day_str, "%b %d %H:%M:%S")
            
            # Current year for complete datetime
            timestamp = timestamp.replace(year=datetime.now().year)

            # Hostname, process, and message components
            hostname = parts[3]
            process = parts[4].split(":")[0]  # Process name (e.g., su, CRON)
            message = parts[5]
            
            ips = self.ip_pattern.findall(message)
            
            

            # Determine severity or type from keywords in the message
            if "FAILED" in message:
                event_type = "Authentication Failure"
            elif "authentication failure" in message:
                event_type = "Auth Failure (PAM)"
            elif "session opened" in message:
                event_type = "Session Opened"
            elif "session closed" in message:
                event_type = "Session Closed"
            else:
                event_type = "Other"

            # Return structured log information
            return {
                "timestamp": timestamp,
                "host": hostname,
                "process": process,
                "event_type": event_type,
                "message": message,
                "ips": None if len(ips) == 0 else ips[0]
            }
        except (IndexError, ValueError):
            return None

