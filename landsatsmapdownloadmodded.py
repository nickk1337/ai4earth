import tarfile
from datetime import date
import requests
import wget
import os

from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer

global tries, flag
count = 0


def getsmap(d):
    global tries, flag
    dey = d + 4
    # String Manipulation for correct File Name
    if 9 < d < 100:
        day_n = '0' + str(d)
    elif d < 10:
        day_n = '00' + str(d)
    elif 99 < d < 367:
        day_n = str(d)
    else:
        flag = -1
        return -1

    #String Manipulation for correct URL
    if 9 < dey < 100:
        dey_n = '0' + str(dey)
    elif dey < 10:
        dey_n = '00' + str(dey)
    elif 99 < dey < 371:
        dey_n = str(dey)
    else:
        flag = -1
        return -1

    #File location and File naming specifics so other scripts
    dataset_location = str(yr) + '/' + day_n
    dataset_name = 'RSS_smap_SSS_L3_8day_running_' + str(yr) + '_' + dey_n + '_FNL_v04.0.nc'
    url = 'https://podaac-opendap.jpl.nasa.gov/opendap/allData/smap/L3/RSS/V4/8day_running/SCI/' + dataset_location + '/' + dataset_name
    save_location = 'C:/Users/MLMan/Desktop/SMAP Download/' + str(yr) + '/' + line + '/'
    r = requests.head(url, allow_redirects=True, )
    if r.status_code == 404:
        tries = tries + 1
        if tries < 5:
            getsmap(d + 1) #Checking if there is SMAP data for the next 5 days
        else:
            flag = -2
            return -1

    else:
        save_file = save_location + dataset_name
        is_exist = os.path.exists(save_location)
        if not is_exist:
            os.makedirs(save_location)
        if not(os.path.exists(save_file) or os.path.exists((save_location + line + '.nc'))):
            wget.download(url, save_file)
            os.rename(save_file, (save_location + line + '.nc'))


api = API('swetha123', 'abcdef123456')  # username ,password
scenes = api.search(
    dataset='landsat_8_c1',
    latitude=13.0149,
    longitude=74.1607,
    # bbox=(74.408,  13.397,  74.660,  13.640),
    start_date='2016-01-01',
    end_date='2016-12-31',
    max_cloud_cover=9
)

print(f"{len(scenes)} scenes found.")

with open("output.txt", "w") as f:
    for scene in scenes:
        f.write(scene['landsat_product_id'])
        f.write("\n")

ee = EarthExplorer('swetha123', 'abcdef123456')
with open("output.txt", "r") as f:
    line = f.readline()[:-1]

    while line:
        flag = 0
        #Extract date from filename
        yr = int(line[17:21])
        mon = int(line[21:23])
        dy = int(line[23:25])
        doy = date(yr, mon, dy).timetuple().tm_yday
        tries = 0
        getsmap(doy)

        #Code to check if there is SMAP data for Landsat file
        if flag == -1 or flag == -2:
            if flag == -1:
                print('No SMAP for', line, 'scene in', yr)
            if flag == -2:
                print('No SMAP for', line, 'scene or the next', tries, 'days')
            print('Skipping', line, 'scene\n')
            line = f.readline()[:-1]
            continue

        output_dir = 'C:/Users/MLMan/Desktop/Landsat Download/' + str(yr) + '/'
        is_exist = os.path.exists(output_dir)

        #Code to extract tar.gz files
        if not is_exist:
            os.makedirs(output_dir)
        if not(os.path.exists(output_dir + line + '.tar.gz')):
            ee.download(line, output_dir)
            file = tarfile.open(output_dir + line + '.tar.gz')
            file.extractall(output_dir + line + '/')
            file.close()

            #To remove bands 1, 6-12, BQA to save space
            for i in range (6,12):
                os.remove(output_dir + line + '/' + line + '_B' + str(i) +'.tif')
            os.remove(output_dir + line + '/' + line + '_BQA.tif')
            os.remove(output_dir + line + '/' + line + '_B1.tif')
            os.remove(output_dir + line + '.tar.gz')
            count += 1
            line = f.readline()[:-1]
        
ee.logout()
api.logout()
print('\n', count, 'Downloads Complete')
