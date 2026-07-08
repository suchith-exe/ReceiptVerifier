import pandas as pd


class CSVLoader:

    def __init__(self, filename):
        self.filename = filename
        self.database = {}

    def load(self):

        df = pd.read_csv(self.filename)

        # Remove spaces from column names
        df.columns = df.columns.str.strip()

        for _, row in df.iterrows():

            consumer = str(row["Consumer No"]).strip().upper()

            self.database[consumer] = {
                "name": row["Customer Name"],
                "date": row["Delivery Date"],
                "mobile": row["Customer Mobile Number"]
            }

        print(f"\nLoaded {len(self.database)} consumers.")

        return self.database