from lookup.csv_loader import CSVLoader

loader = CSVLoader("data/Delivery Register Report.csv")
loader.load()

booking = input("Booking No: ")

record = loader.find_booking(booking)

if record:
    print(record)
else:
    print("Not Found")