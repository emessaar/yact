#fileds.py
from sqlalchemy import create_engine
import pandas as pd
chunksize = 50000
def prep_df(df):
  df = df.rename(columns={c: c.replace(' ', '_') for c in df.columns})
  df = df.rename(columns={c: c.replace('.', '_') for c in df.columns})
  return df

class FileDS(object):
  def __init__(self, dbpath=None):
    self.diskdb = create_engine('sqlite:///' + dbpath)

  def load_dataset(self, tablename=None, dataset_path=None):
    df = pd.read_csv(dataset_path, encoding='utf-8')
    prep_df(df).to_sql(tablename, self.diskdb, if_exists='replace')

  def query_to_df(self, query):
    df = pd.read_sql_query(query, self.diskdb)
    return df

  def query_to_rc(self, query):
    df = pd.read_sql_query(query, self.diskdb)
    return list(df.to_records(index=False)), tuple(df.columns)

