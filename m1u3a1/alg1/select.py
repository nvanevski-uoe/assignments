import time
import sys
from loadflights import load_flights


def select_lowest_price_flights(flight_results):
    """
    Given a list of FlightResult records, returns a new list containing only the lowest price record for each unique key.
    Also returns the number of milliseconds elapsed during the operation.
    Assumes FlightResult has 'key' and 'price' attributes.
    This version uses a quadratic scan and does not use maps.
    """
    start_time = time.time()
    result_list = []
    processed_keys = set()

    for i, record in enumerate(flight_results):
        key = record.key
        if key in processed_keys:
            continue

        lowest_record = record
        for j in range(len(flight_results)):
            if j == i:
                continue
            other = flight_results[j]
            if other.key == key and other.price < lowest_record.price:
                lowest_record = other
        result_list.append(lowest_record)
        processed_keys.add(key)

    elapsed_ms = int((time.time() - start_time) * 1000)
    return result_list, elapsed_ms


def select_lowest_price_flights_map(flight_results):
    """
    Given a list of FlightResult records, returns a new list containing only the lowest price record for each unique key.
    Also returns the number of milliseconds elapsed during the operation.
    This version uses a map (dictionary) for efficient lookup.
    Assumes FlightResult has 'key' and 'price' attributes.
    """
    start_time = time.time()
    lowest_price_map = {}

    for record in flight_results:
        key = record.key
        if key not in lowest_price_map or record.price < lowest_price_map[key].price:
            lowest_price_map[key] = record

    result_list = list(lowest_price_map.values())
    elapsed_ms = int((time.time() - start_time) * 1000)
    return result_list, elapsed_ms


def select_lowest_price_flights_sort_sweep(flight_results):
    """
    Given a list of FlightResult records, returns a new list containing only the lowest price record for each unique key.
    Also returns the number of milliseconds elapsed during the operation.
    This version uses a sort-and-sweep algorithm.
    Assumes FlightResult has 'key' and 'price' attributes.
    """
    start_time = time.time()

    sorted_flights = sorted(flight_results, key=lambda r: r.key)
    result_list = []
    prev_key = None
    lowest_record = None

    for record in sorted_flights:
        if record.key != prev_key:
            if lowest_record is not None:
                result_list.append(lowest_record)
            lowest_record = record
            prev_key = record.key
        else:
            if record.price < lowest_record.price:
                lowest_record = record
    if lowest_record is not None:
        result_list.append(lowest_record)

    elapsed_ms = int((time.time() - start_time) * 1000)
    return result_list, elapsed_ms


def main():
    if len(sys.argv) != 2:
        print("Usage: python select.py <filename>")
        return

    filename = sys.argv[1]
    flight_results = load_flights(filename)

    _, elapsed_ms_quad = select_lowest_price_flights(flight_results)
    print(f"Quadratic scan execution time: {elapsed_ms_quad} ms")
    print(f"Number of unique flights (quadratic): {len(_)}")

    _, elapsed_ms_sort = select_lowest_price_flights_sort_sweep(flight_results)
    print(f"Sort-and-sweep execution time: {elapsed_ms_sort} ms")
    print(f"Number of unique flights (sort-and-sweep): {len(_)}")

    _, elapsed_ms_map = select_lowest_price_flights_map(flight_results)
    print(f"Map execution time: {elapsed_ms_map} ms")
    print(f"Number of unique flights (map): {len(_)}")

if __name__ == "__main__":
    main()