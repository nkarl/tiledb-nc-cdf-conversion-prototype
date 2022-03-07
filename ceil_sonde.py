import os, glob, shutil
import netCDF4, tiledb, tiledb.cf
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

cfg = tiledb.Ctx().config()
cfg.update(
    {
        'py.init_buffer_bytes': 1024**2 * 50
    }
)
tiledb.default_ctx(cfg)

# For plotting
marker='o'
linestyle=''
markersize=1

## Data Directory
# ceil_dir = "./data/sgpceilC1.b1"
ceil_dir = os.path.join(os.getcwd(), "data", "sgpceilC1.b1")

# sonde_dir = "./data/sgpsondewnpnC1.b1"
sonde_dir = os.path.join(os.getcwd(), "data", "sgpsondewnpnC1.b1")

## ---> COMMENT THIS OUT ONCE TESTING IS DONE
# backup seed files
# backup_seed_ceil = "./sgpceilC1.b1/20200801.000015.nc"
backup_seed_ceil = os.path.join(os.getcwd(), "sgpceilC1.b1", "20200801.000015.nc")
# backup_seed_sonde = "./sgpsondewnpnC1.b1/20201101.232500.cdf"
backup_seed_sonde = os.path.join(os.getcwd(), "sgpsondewnpnC1.b1", "20201101.232500.cdf")

shutil.rmtree(ceil_dir, ignore_errors=True)
shutil.rmtree(sonde_dir, ignore_errors=True)
os.mkdir(ceil_dir)
os.mkdir(sonde_dir)
# os.mkdir(ceil_group_uri)
# os.mkdir(sonde_group_uri)
shutil.copy2(backup_seed_ceil, f"{ceil_dir}")
shutil.copy2(backup_seed_sonde, f"{sonde_dir}")
## <--- COMMENT THIS OUT ONCE TESTING IS DONE

ceil_files = glob.glob(f"{ceil_dir}/*")
ceil_files.sort()
ceil_file = ceil_files[0]
# print(f"ceil file path : {ceil_file}")

sonde_files = glob.glob(f"{sonde_dir}/*")
sonde_files.sort()
sonde_file = sonde_files[0]
# print(f"sonde file path: {sonde_file}")

ceil_group_uri = f"{ceil_file}.tdb"
print(f"ceil group uri : {ceil_group_uri}")
sonde_group_uri = f"{sonde_file}.tdb"
print(f"sonde group uri: {sonde_group_uri}")

ceil_converter = tiledb.cf.NetCDF4ConverterEngine(ceil_file)
ceil_converter = tiledb.cf.NetCDF4ConverterEngine.from_file(
    ceil_file,
    dim_dtype=np.uint32,
    attrs_filters=[tiledb.ZstdFilter(level=7)],
)
# # ceil_converter
# ceil_converter.convert_to_group(ceil_group_uri)

# # ceil_group_schema = tiledb.cf.GroupSchema.load(ceil_group_uri)
# # ceil_group_schema

# with tiledb.cf.Group(ceil_group_uri) as ceil_group:
    # with (
        # ceil_group.open_array(attr="first_cbh") as first_cbh,
        # ceil_group.open_array(attr="detection_status") as detection_status,
    # ):
        # first_cbh_series = first_cbh[:]
        # detection_status_series = detection_status[:]

# COMMENT: this only works with Python 3.9+
# REQUIRED: python -m pip install --upgrade pip jupyterlab

# plt.plot(first_cbh_series)
# plt.plot(detection_status_series)
# plt.show()

# sonde_converter = tiledb.cf.NetCDF4ConverterEngine(nc_file)
sonde_converter = tiledb.cf.NetCDF4ConverterEngine.from_file(
    sonde_file,
    dim_dtype=np.uint32,
    attrs_filters=[tiledb.ZstdFilter(level=7)],
)
# sonde_converter

import logging
LOG_FILE = "./error_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

try:
    sonde_converter.convert_to_group(sonde_group_uri)
except:
    logging.exception("!!! ERROR DETECTED. POSSIBLY CAUSE: FILEPATH TOO LONG !!!")
    raise

# sonde_group_schema = tiledb.cf.GroupSchema.load(sonde_group_uri)
# sonde_group_schema

# with tiledb.cf.Group(sonde_group_uri) as sonde_group:
    # with (
        # sonde_group.open_array(attr="first_cbh") as first_cbh,
        # sonde_group.open_array(attr="detection_status") as detection_status,
    # ):
        # first_cbh_series = first_cbh[:]
        # detection_status_series = detection_status[:]

# # COMMENT: this only works with Python 3.9+
# # REQUIRED: python -m pip install --upgrade pip jupyterlab

# # plt.plot(first_cbh_series)
# # plt.plot(detection_status_series)
# # plt.show()
