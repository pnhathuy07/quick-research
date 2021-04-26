import pandas as pd
df = pd.DataFrame({'a': [1, 2, 1, 5,6,7,7,9,9,8,9], 'b': [1, 2, 3, 5,6,5,3,3,5,5,5]})

print(df)

df['count'] = df.groupby('a')['a'].transform(pd.Series.count())
df.sort('count', ascending=False)

print(df)