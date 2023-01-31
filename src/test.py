from osgeo import gdal
import pandas as pd

df = pd.read_parquet("s3://mhw-2022/preprocessed/ais/ihs/position-history/5_min/default/date=2021-10-20/20211020000100_data.parquet.gzip")
