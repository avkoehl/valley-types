import re
import xml.etree.ElementTree as et

from bs4 import BeautifulSoup as bs
import pandas as pd
import geopandas as gpd 
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from shapely.geometry import box

# workflow:
#  download metadata for dataset
#  create csv
#  define a bounding box
#  intersect that bounding box with the metadata dataset
#  download the relevant tiff files
#  mosiac
#  crop to bounding box

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

def filter_data(metadf, bbox):
    """ 
    Filter metadata rows to exclude any rows that are not intersecting with 
    the supplied bounding box
    """
    return metadf.loc[metadf.intersects(bbox)]

def download_tiffs(tiff_url_series, odir):
    """ 
    Download each tiff file from the list of tiff urls and save in the 
    output directory
    """
    for url in tiff_url_series:
        data = requests.get(url).content
        with open(odir + '/' + url.split('/')[-1], 'wb') as handle:
            handle.write(data)
    return

def mosaic_and_crop(odir):
    return

def main():
    minx = -121.23
    miny = 38.23
    maxx = -120.286
    maxy = 39.29

    odir = "./"


    meta = create_metadata_df()
    filtered = filter_data(meta, box(minx, miny, maxx, maxy))
    download_tiffs(filtered['tiff_url'], ".")
    full = mosiac_and_crop(odir)

