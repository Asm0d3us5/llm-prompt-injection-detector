from datasets import load_dataset
import pandas as pd

ds1 = load_dataset("deepset/prompt-injections", split="train")
ds2 = load_dataset("JasperLS/prompt-injections", split="train")

df1 = pd.DataFrame(ds1)[["text", "label"]]
df1["source"] = "deepset"

df2 = pd.DataFrame(ds2)[["text", "label"]]
df2["source"] = "jasperls"

combined = pd.concat([df1, df2], ignore_index=True)
combined.to_csv("data/hf_combined.csv", index=False)
print(f"Saved {len(combined)} samples")
