import csv
import time

class Log:
    
    def __init__(self, start_time=0, filename='AIRPG_LOG.csv') -> None:
        self.start_time = start_time
        self.filename = filename
        self.create_csv()

    def create_csv(self):
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Game Time", "Text"])

    def log(self, text: str):
        current_time = time.time() - self.start_time
        game_time = time.strftime("%H:%M:%S", time.gmtime(current_time))
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([game_time, text])
