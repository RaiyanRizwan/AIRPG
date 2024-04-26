import os
import csv
import time

class Log:
    
    def __init__(self, start_time=0, disabled=False, foldername='logs') -> None:
        self.start_time = start_time
        self.foldername = foldername
        self.disabled = disabled
        self.filename = ''
        if not disabled:
            self.filename = self.setup_file()
            self.create_csv()

    def setup_file(self):
        if self.disabled:
            return
        os.makedirs(self.foldername, exist_ok=True)
        existing_logs = [log for log in os.listdir(self.foldername) if log.startswith("AIRPG_LOG_") and log.endswith(".csv")]
        log_number = len(existing_logs) + 1
        return os.path.join(self.foldername, f'AIRPG_LOG_{log_number}.csv')
    
    def create_csv(self):
        if self.disabled:
            return
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Game Time", "Text"])

    def log(self, text: str):
        if self.disabled:
            return
        current_time = time.time() - self.start_time
        game_time = time.strftime("%H:%M:%S", time.gmtime(current_time))
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([game_time, text])
    
    @staticmethod
    def clear_logs():
        dir = './logs'
        if not os.path.exists(dir):
            return
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            os.remove(file_path)