import json
import os
class DataBase:
    def __init__(self, file_path = "data.json"):
        self.file_path = file_path
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as file:
                    self.data = json.load(file)
                    print(f"Data loaded from {self.file_path}.")
            except json.JSONDecodeError:
                print(f"Error decoding JSON in {self.file_path}. Starting with an empty database.")
                self.data = {}
        else:
            self.save() 
    def save(self):
        try:
            with open(self.file_path, "w") as file:
                json.dump(self.data, file, indent=4)
                print(f"Data saved to {self.file_path}.")
        except Exception as e:
            print(f"Error saving data to {self.file_path}: {e}")

    def insert(self, key, value):
        self.data[key] = value
        self.save()

    def search(self, key, default=None):
        return self.data.get(key, default)

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self.save()
        else:
            print(f"Key '{key}' not found.")

    def clear(self):
        self.data = {}
        self.save()