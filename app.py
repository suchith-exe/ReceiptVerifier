from csv_loader import CSVLoader

loader = CSVLoader("data/Delivery Register Report.csv")

database = loader.load()

print("\nReceipt Verifier Started!")
print("Type EXIT to quit.\n")

while True:

    consumer = input("Consumer No : ").strip().upper()

    if consumer == "EXIT":
        break

    if consumer in database:

        print("\n✅ FOUND")

        print("Customer :", database[consumer]["name"])
        print("Delivery :", database[consumer]["date"])
        print("Mobile   :", database[consumer]["mobile"])

    else:

        print("\n❌ NOT FOUND")

    print()