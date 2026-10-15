import pandas as pd

df = pd.read_excel("data.xlsx", sheet_name="RPA", skiprows=2, header=None, usecols="A:D", names=["voltage 1", ""])

print(df.to_markdown())
