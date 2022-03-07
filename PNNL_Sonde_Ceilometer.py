#!/usr/bin/env python
# coding: utf-8

import os
import glob
import xarray as xr
import tiledb
import matplotlib.pyplot as plt, numpy as np, pandas as pd

cfg = tiledb.Ctx().config()
cfg.update(
    {
        'py.init_buffer_bytes': 1024**2 * 50
    }
)
# tiledb.default_ctx(cfg)

# For plotting
marker='o'
linestyle=''
markersize=1
## Data Directory
ceil_dir = "./data/sgpceilC1.b1"
ceil_files = glob.glob(f"{ceil_dir}/*")
ceil_files.sort()
ceil_file = ceil_files[0]

sonde_dir = "./data/sgpsondewnpnC1.b1"
sonde_files = glob.glob(f"{sonde_dir}/*")
sonde_files.sort()
sonde_file = sonde_files[0]

## Load single ceil file
# %%time
ceil_dataset = xr.open_dataset(ceil_file)
# ceil_dataset['detection_status']
first_cbh = ceil_dataset['first_cbh']
first_cbh.plot()
detection_status = ceil_dataset['detection_status']
detection_status.plot()
plt.show()
## Load multiple ceil files
# %%time
ceil_mfdataset = xr.open_mfdataset(ceil_files)
ceil_times =  ceil_mfdataset['time']
first_cbh = ceil_mfdataset['first_cbh']
second_cbh = ceil_mfdataset['second_cbh']
detection_status = ceil_mfdataset['detection_status']
fig, ax = plt.subplots(figsize=(15, 5))
first_cbh.plot(marker=marker, linestyle=linestyle, markersize=markersize)
fig, ax = plt.subplots(figsize=(15, 5))
first_cbh.plot(marker=marker, linestyle=linestyle, markersize=markersize)
second_cbh.plot(marker=marker, linestyle=linestyle, markersize=markersize)

plt.legend(["Ceil First CBH", "Ceil Second CBH"])
fig, ax = plt.subplots(figsize=(15, 5))
detection_status.plot(marker=marker, linestyle=linestyle, markersize=markersize)
# detection_status where at least one cloud base detected
one_cloud = 1
detection_status_data = detection_status.data

# At lest one cloud: flag values of 1, 2, or 3
lower_bound = detection_status_data >= 1
upper_bound =  detection_status_data < 4
at_least_one_cloud = lower_bound * upper_bound

# Times where at least one cloud
ceil_cloud_times = ceil_times[at_least_one_cloud]
## Load mulitple sonde data
# %%time
sonde_mfdataset = xr.open_mfdataset(sonde_files)
sonde_times = sonde_mfdataset['time']
sonde_alt = sonde_mfdataset['alt']
sonde_temp = sonde_mfdataset['tdry']
sonde_pres = sonde_mfdataset['pres']
sonde_wspd = sonde_mfdataset['wspd']
## Retrieve Sonde times where there is at least one CBH in ceil data
# Sonde times where there is at least one CBH in ceil 
good_sonde_times = sonde_times.isin(ceil_cloud_times)

overlap_sonde_times = sonde_times[good_sonde_times]
overlap_sonde_alt = sonde_alt[good_sonde_times]
overlap_sonde_temp = sonde_temp[good_sonde_times]
overlap_sonde_pres = sonde_pres[good_sonde_times]
overlap_sonde_wspd = sonde_wspd[good_sonde_times]
fig, ax = plt.subplots(figsize=(15, 5))
overlap_sonde_alt.plot(marker=marker, linestyle=linestyle, markersize=markersize)
first_cbh.plot(marker=marker, linestyle=linestyle, markersize=markersize)
second_cbh.plot(marker=marker, linestyle=linestyle, markersize=markersize)

plt.legend(["Sonde Alt", "Ceil First CBH", "Ceil Second CBH"])
## Retrieve times where sonde balloon is at or above CBH

# Times in cbh that are also in sonde
cbh_overlap_sonde = ceil_cloud_times.isin(overlap_sonde_times)

# CBH overlaps with sonde (timewise)
tmp_cbh = first_cbh[at_least_one_cloud]
overlap_cbh = tmp_cbh[cbh_overlap_sonde]

# now, only keep times where the sonde ballon is at or above the cloud base height
sonde_above_cbh = overlap_sonde_alt >= overlap_cbh
# Plot the sonde alt and cbh where the sonde ballon is at or above the cloud base height
fig, ax = plt.subplots(figsize=(15, 5))

overlap_sonde_alt[sonde_above_cbh].plot(marker=marker, linestyle=linestyle, markersize=markersize)
overlap_cbh[sonde_above_cbh].plot(marker=marker, linestyle=linestyle, markersize=markersize)
# Get the windspeed, temperature, and pressure values where the sonde balloon is at or above the first cloud base height
above_cbh_sonde_temp = overlap_sonde_temp[sonde_above_cbh]
above_cbh_sonde_pres = overlap_sonde_pres[sonde_above_cbh]
above_cbh_sonde_wspd = overlap_sonde_wspd[sonde_above_cbh]
# Plot the windspeed
fig, ax = plt.subplots(figsize=(15, 5))
above_cbh_sonde_wspd.plot(marker=marker, linestyle=linestyle, markersize=markersize)
## Plot a couple of days
start_time = "2020-09-01" # Inclusive
end_time = "2020-09-05" # Inclusive
time_range = slice(start_time, end_time)
fig, ax = plt.subplots(figsize=(15, 5))

alt = overlap_sonde_alt[sonde_above_cbh].sel(time=time_range)
alt.plot(marker=marker, linestyle=linestyle, markersize=markersize)

cbh = overlap_cbh[sonde_above_cbh].sel(time=time_range)
cbh.plot(marker=marker, linestyle=linestyle, markersize=markersize)

plt.legend(["Sonde Alt", "Ceil First CBH"])

# Plot the temperature
fig, ax = plt.subplots(figsize=(15, 5))

temp = above_cbh_sonde_temp.sel(time=time_range)
temp.plot(marker=marker, linestyle=linestyle, markersize=markersize)
# Plot the pressure
fig, ax = plt.subplots(figsize=(15, 5))

pressure = above_cbh_sonde_pres.sel(time=time_range)
pressure.plot(marker=marker, linestyle=linestyle, markersize=markersize)

