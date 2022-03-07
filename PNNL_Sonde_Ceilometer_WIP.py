#!/usr/bin/env python
# coding: utf-8

import os, glob, shutil
import netCDF4, tiledb, tiledb.cf
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

cfg = tiledb.Ctx().config()
cfg.update(
    {
        'py.init_buffer_bytes': 1024**2 * 50
    }
)
#tiledb.default_ctx(cfg)

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
#
## NOTE: the following section reset the data directory.
#
# backup seed files
# backup_seed_ceil = "./sgpceilC1.b1/20200801.000015.nc"
backup_seed_ceil = os.path.join(os.getcwd(), "sgpceilC1.b1", "20200801.000015.nc")
# backup_seed_sonde = "./sgpsondewnpnC1.b1/20201101.232500.cdf"
backup_seed_sonde = os.path.join(os.getcwd(), "sgpsondewnpnC1.b1", "20201101.232500.cdf")
shutil.rmtree(ceil_dir, ignore_errors=True)
shutil.rmtree(sonde_dir, ignore_errors=True)
os.makedirs(ceil_dir, exist_ok=True)
os.makedirs(sonde_dir, exist_ok=True)
# copy the seed datafiles to the data directory
shutil.copy2(backup_seed_ceil, f"{ceil_dir}")
shutil.copy2(backup_seed_sonde, f"{sonde_dir}")
#
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
# print(f"ceil group uri : {ceil_group_uri}")
sonde_group_uri = f"{sonde_file}.tdb"
# print(f"sonde group uri: {sonde_group_uri}")

import cProfile
cpf = cProfile.Profile()


# profiles the conversion process for nc
cpf.enable()
ceil_converter = tiledb.cf.NetCDF4ConverterEngine(ceil_file)
ceil_converter = tiledb.cf.NetCDF4ConverterEngine.from_file(
    ceil_file,
    dim_dtype=np.uint32,
    attrs_filters=[tiledb.ZstdFilter(level=7)],
)
# # ceil_converter
ceil_converter.convert_to_group(ceil_group_uri)

# # ceil_group_schema = tiledb.cf.GroupSchema.load(ceil_group_uri)
# # ceil_group_schema

cpf.disable()
cpf.print_stats('cumtime')

## profiles the query performance on ceil_group
cpf.enable()

# NOTE: the following section only works with Python 3.9+
with tiledb.cf.Group(ceil_group_uri) as ceil_group:
    with (
        ceil_group.open_array(attr="first_cbh") as first_cbh,
        ceil_group.open_array(attr="second_cbh") as second_cbh,
        ceil_group.open_array(attr="detection_status") as detection_status,
    ):
        first_cbh_series = first_cbh[:]
        second_cbh_series = second_cbh[:]
        detection_status_series = detection_status[:]

plt.plot(first_cbh_series, marker=marker, linestyle=linestyle, markersize=markersize)
plt.plot(second_cbh_series, marker=marker, linestyle=linestyle, markersize=markersize)
plt.plot(detection_status_series, marker=marker, linestyle=linestyle, markersize=markersize)
plt.show()

cpf.disable()
cpf.print_stats('cumtime')

## profiles the conversion process for cdf
cpf.enable()
# # sonde_converter
sonde_converter = tiledb.cf.NetCDF4ConverterEngine.from_file(
    sonde_file,
    dim_dtype=np.uint32,
    attrs_filters=[tiledb.ZstdFilter(level=7)],
)
# sonde_converter

## <--- this section is guard for when filepath length exceeds maximum allowed length.
import logging
LOG_FILE = "./error_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
try:
    sonde_converter.convert_to_group(sonde_group_uri)
except:
    logging.exception("!!! ERROR DETECTED. POSSIBLY CAUSE: FILEPATH TOO LONG !!!")
    raise
## ---> end exception guard.

# sonde_group_schema = tiledb.cf.GroupSchema.load(sonde_group_uri)
# sonde_group_schema

cpf.disable()
cpf.print_stats('cumtime')

## profiles the query performance on sonde_group
cpf.enable()

with tiledb.cf.Group(sonde_group_uri) as sonde_group:
    with (
        sonde_group.open_array(attr="alt") as alt_,
        sonde_group.open_array(attr="tdry") as tdry,
        sonde_group.open_array(attr="pres") as pres,
        sonde_group.open_array(attr="wspd") as wspd,
    ):
        alt_series = alt_[:]
        tdry_series = tdry[:]
        pres_series = pres[:]
        wspd_series = wspd[:]
    

# # COMMENT: this only works with Python 3.9+
# # REQUIRED: python -m pip install --upgrade pip jupyterlab

plt.plot(alt_series, marker=marker, linestyle=linestyle, markersize=markersize)
plt.plot(tdry_series, marker=marker, linestyle=linestyle, markersize=markersize)
plt.plot(pres_series, marker=marker, linestyle=linestyle, markersize=markersize)
plt.plot(wspd_series, marker=marker, linestyle=linestyle, markersize=markersize)
plt.show()

cpf.disable()
cpf.print_stats('cumtime')

