import pandas as pd
import os

l = []


for f in os.listdir("/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/results"):
    l.append(pd.read_csv(f"./results/{f}"))

df_res = pd.concat(l, axis=1, ignore_index=True)
df_res.to_csv("global.csv", sep=",")
