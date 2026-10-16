import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("data.xlsx", sheet_name="RPA", skiprows=4, header=None, usecols="A:D", names=["V1", "A1", "V2", "A2"])

df = df.apply(pd.to_numeric, errors="coerce")

print(df["V1"])
print(df["A1"])

df.plot(x="V1", y="A1")

plt.show()
#
# print(df)
