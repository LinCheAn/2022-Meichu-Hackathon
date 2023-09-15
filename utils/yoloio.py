# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 16:52:36 2021

@author: JWCHANGT
"""

import os
import shutil
import yaml

def tempfolder_get(path):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)
    else:
        os.makedirs(path, exist_ok=True)
        
def yaml_reader(path):
    with open(path, 'r', encoding="utf-8") as fp:
        config = yaml.load(fp, Loader = yaml.FullLoader)
    return config

def yaml_writer(data, path):
    with open(path, 'w') as handle:
        yaml.safe_dump(data, handle, default_flow_style=None, sort_keys=False)
        
def txt_writer(distPath,distfilename,obj,defectcode,height,width):
    path = distPath + '/' + distfilename
    with open(path, 'w') as f:
        for objtemp in obj:
            objname = objtemp['name']
            objxmin = objtemp['xmin']
            objxmax = objtemp['xmax']
            objymin = objtemp['ymin']
            objymax = objtemp['ymax']
            objidx_output = defectcode.index(objname)
            objxc_output = (objxmax + objxmin)/2/width
            objyc_output = (objymax + objymin)/2/height
            objxsiz_output = (objxmax-objxmin+1)/width
            objysiz_output = (objymax-objymin+1)/height
            f.write('{} {:.6f} {:.6f} {:.6f} {:.6f}\n'.format(objidx_output,objxc_output,objyc_output,objxsiz_output,objysiz_output))
            
            
            