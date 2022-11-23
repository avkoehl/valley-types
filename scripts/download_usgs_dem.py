# brew install gdal
# brew install geckodriver

import os
import sys
import re
import xml.etree.ElementTree as et

from bs4 import BeautifulSoup as bs
import pandas as pd
import geopandas as gpd 
import rasterio
from rasterio.mask import mask
from rasterio.merge import merge
from rasterio.plot import show
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from shapely.geometry import box

# useful tool for creating a bounding box: https://boundingbox.klokantech.com/

# workflow:
#  download metadata for dataset (name, xmlfilepath, datafilepath, minx, miny, maxx, maxy)
#  filter dataset based on intersection with user provided bounding box 
#  download the relevant tiff files
#  merge and crop to the bounding box
#  save the combined file

# alternate workflow: 
#    Use the interface at https://apps.nationalmap.gov/downloader/


def create_metadata_df():
    """ 
    From the index page and the base url create a dataframe of all the 
    metadata for each tiff file in the dataset
    """

    index = "https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Elevation/13/TIFF/current/"
    base = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/"

    def parse_tilename(name):
        """ Given name list n6e162 return the extent and dl links """
        lat = float(name[0:3].replace('n','').replace('s','-'))
        lng = float(name[3:7].replace('w','-').replace('e',''))
        # w170 -> -169:-170
        # s14  -> -14:-15 no idea why
        if lng < 0:
            minx = lng + 0.99
        else:
            minx = lng - .99

        b = box(minx, lat-1, lng, lat)
        return {
                'ID': name,
                'meta_url': base + name + "USGS_13_" + name[:-1] + ".xml",
                'tiff_url': base + name + "USGS_13_" + name[:-1] + ".tif",
                'area': b
        }

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    content = driver.get(index)
    html = driver.page_source
    driver.close()
    soup = bs(html, 'html.parser')

    names = [l.text for l in soup.find_all('a') if 
                  re.search('[ns]\d{2}[ew]\d{3}', l['href'])]
    parsed = [parse_tilename(n) for n in names]
    df = gpd.GeoDataFrame.from_records(parsed)
    df = df.set_geometry("area")
    df = df.set_index("ID")
    return  df


def download_tiffs(tiff_url_series, odir):
    """ 
    Download each tiff file from the list of tiff urls and save in the 
    output directory
    """
    ofiles = []
    for url in tiff_url_series:
        data = requests.get(url).content
        with open(odir + '/' + url.split('/')[-1], 'wb') as handle:
            ofiles.append(handle.name)
            handle.write(data)
    return ofiles

def main():
    minx = -122.57
    miny = 37.81
    maxx = -122.45
    maxy = 37.87

    ofile = f"../raw_data/USGS13:{minx}_{miny}_{maxx}_{maxy}.tif"

    meta = create_metadata_df()
    filtered = meta.loc[meta.intersects(box(minx,miny,maxx,maxy))]
    tif_files = download_tiffs(filtered['tiff_url'], ".")

    if not tif_files:
        sys.exit(f"No DEM Files found for {minx} {miny} {maxx} {maxy}")

    combined = merge(tif_files, bounds=(minx, miny, maxx, maxy), dst_path=ofile)


    # clean up
    for f in tif_files:
        if os.path.exists(f):
            os.remove(f)

    if os.path.exists("geckodriver.log"):
        os.remove("geckodriver.log")

    # show(combined)  # to make sure it worked

if __name__ == "__main__":
    main()
