class FlightResult:
    def __init__(self, outgoing_flight_number, origin_airport,
                 destination_airport, layover_airport, duration, price):
        self.outgoing_flight_number = outgoing_flight_number
        self.origin_airport = origin_airport
        self.destination_airport = destination_airport
        self.layover_airport = layover_airport
        self.duration = duration
        self.price = price
        self.key = self.generateKey()

    def generateKey(self):
        return f"{self.origin_airport}_{self.layover_airport}_{self.destination_airport}_{self.duration}"

    # Getters
    def get_outgoing_flight_number(self):
        return self.outgoing_flight_number

    def get_origin_airport(self):
        return self.origin_airport

    def get_destination_airport(self):
        return self.destination_airport

    def get_layover_airport(self):
        return self.layover_airport

    def get_duration(self):
        return self.duration

    def get_price(self):
        return self.price

    # Setters
    def set_outgoing_flight_number(self, value):
        self.outgoing_flight_number = value

    def set_origin_airport(self, value):
        self.origin_airport = value

    def set_destination_airport(self, value):
        self.destination_airport = value

    def set_layover_airport(self, value):
        self.layover_airport = value

    def set_duration(self, value):
        self.duration = value

    def set_price(self, value):
        self.price = value