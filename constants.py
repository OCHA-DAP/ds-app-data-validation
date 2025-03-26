import os

import ocha_stratus as stratus
import pandas as pd

STAGE = os.getenv("STAGE")
engine = stratus.get_engine(STAGE)

# TODO: Don't love global df here -- should put into a store
with engine.connect() as conn:
    DF_ISO3 = pd.read_sql("select iso3, max_adm_level from iso3", con=conn)

ISO3S = list(DF_ISO3.iso3)
