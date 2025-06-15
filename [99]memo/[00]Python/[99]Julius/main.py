# Load dataset and analyze relationship between Age and Quality of Sleep across occupations
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read CSV
file_path = 'Sleep_health_and_lifestyle_dataset.csv'
df = pd.read_csv(file_path, encoding='ascii')

# Quick look at data
print(df.head())

# Compute correlation between Age and Quality of Sleep for each Occupation
corr_by_occ = df.groupby('Occupation').apply(lambda x: x['Age'].corr(x['Quality of Sleep']))
print(corr_by_occ.head())

# Plot scatter with regression lines by occupation using FacetGrid
sns.set(style='whitegrid')
g = sns.lmplot(data=df, x='Age', y='Quality of Sleep', hue='Occupation', scatter_kws={'alpha':0.5}, height=6, aspect=1.5)
plt.title('Age vs Quality of Sleep by Occupation')
plt.show()