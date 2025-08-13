import csv
from flightresult import FlightResult

def load_flights(csv_path):
    results = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            flight = FlightResult(**row)
            results.append(flight)
    return results