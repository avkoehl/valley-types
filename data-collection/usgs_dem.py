import pandas as pd
from selenium import webdriver
import bs4 as bs

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

URL = "https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Elevation/13/TIFF/current/"
# ^ a bunch of folders each containing a jpg, tif, xml, andn gpkg file
# the xml file contains the metadata for that tile
# tif is the DEM data for that tile (geotiff format)


def create_metadata_df(URL):
    """ 
    Load in the xml metadata and create a dataframe that contains all the 
    metadata records 
    """

    driver = webdriver.Firefox()
    content = driver.get(URL)
    html = driver.page_source
    soup = bs(html, 'html.parser')
    for link in soup.find_all('a'):
        if pattern_match(link):
            # pattern is n or s 2 digits w or e 3 digits
            print(link.text)



    # for each link
    # parse the xml file and append to a dataframe

    return

def filter_data(metadf, bbox):
    """ 
    Filter metadata rows to exclude any rows that are not intersecting with 
    the supplied bounding box
    """
    return

def download_tiffs(tiff_url_list, odir):
    """ 
    Download each tiff file from the list of tiff urls and save in the 
    output directory
    """
    return

def mosaic_and_crop(odir):
    return

def main():
    download_metadata_files()
    meta = create_metadata_df(odir)
    bbox = {}
    filtered = filter_data(meta, bbox)
    download_tiffs(filtered$tiffs)
    full = mosiac_and_crop(odir)




