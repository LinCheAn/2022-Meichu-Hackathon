import os
import xml.etree.ElementTree as ET

def parse_voc_annotation(ann_dir, img_dir, IncludeNormal, cache_name=[]):
    
    all_insts = []
    seen_labels = {}
    
    for ann in sorted(os.listdir(ann_dir)):
        img = {'object':[]}

        try:
            tree = ET.parse(ann_dir + ann)
        except Exception as e:
            print(e)
            print('Ignore this bad annotation: ' + ann_dir + ann)
            continue
        
        for elem in tree.iter():
            if 'filename' in elem.tag:
                img['filename'] = img_dir + os.path.splitext(ann)[0] + os.path.splitext(elem.text)[1]
            if 'width' in elem.tag:
                img['width'] = int(elem.text)
            if 'height' in elem.tag:
                img['height'] = int(elem.text)
            if 'object' in elem.tag or 'part' in elem.tag:
                # initalize obj dict
                obj = {}             
                for attr in list(elem):
                    if 'name' in attr.tag:
                        obj['name'] = attr.text
                        
                        if obj['name'] in seen_labels:
                            seen_labels[obj['name']] += 1
                        else:
                            seen_labels[obj['name']] = 1
                                                    
                    if 'bndbox' in attr.tag:
                        for dim in list(attr):
                            if 'xmin' in dim.tag:
                                obj['xmin'] = int(round(float(dim.text)))
                            if 'ymin' in dim.tag:
                                obj['ymin'] = int(round(float(dim.text)))
                            if 'xmax' in dim.tag:
                                obj['xmax'] = int(round(float(dim.text)))
                            if 'ymax' in dim.tag:
                                obj['ymax'] = int(round(float(dim.text)))
                                
                img['object'] += [obj]

        if IncludeNormal:
            all_insts += [img]
        else:
            if len(img['object']) > 0:
                all_insts += [img]
            


    return all_insts, seen_labels