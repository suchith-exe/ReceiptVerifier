import pandas as pd


class CSVLoader:
    def __init__(self, filename):
        self.filename = filename
        self.database = {}

    def load(self):
        df = pd.read_csv(self.filename)
        df.columns = df.columns.str.strip()

        for _, row in df.iterrows():

            booking = str(row["Book No"]).strip().upper()

            self.database[booking] = {
                "consumer": str(row["Consumer No"]).split("/")[0].strip().upper(),
                "name": row["Customer Name"],
                "date": row["Delivery Date"],
                "mobile": str(row["Customer Mobile Number"]).replace(".0", ""),
            }

        return self.database

    def find_booking(self, booking_no):
        booking_no = booking_no.strip().upper()
        return self.database.get(booking_no)