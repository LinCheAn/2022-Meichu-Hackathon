import argparse
import time
from pathlib import Path
import os
import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
from headAlert import MakeAlert
import datetime
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages, LoadWebcam
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box, color_list
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel

def detect2(source_path, save_dir, model, device, imgsz, conf_thres = 0.25, iou_thres = 0.45):
    
    Path(os.path.join(save_dir, "labels")).mkdir(parents=True, exist_ok=True)
    
    device = select_device(device)
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    half = device.type != 'cpu'  # half precision only supported on CUDA
    
    if half:
        model.half()  # to FP16
        
    # dataset = LoadImages(source_path, img_size=imgsz, stride=stride)
    dataset = LoadWebcam() if source_path =='0' else LoadImages(source_path, img_size=imgsz, stride=stride)
    
    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    # colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]
    colors = color_list()
    
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
        
    t0 = time.time()
    ## tolerence
    thresh = 3
    last = 0
    change = 0
    now = 0
    test  = 10
    counter = thresh
    ##timer
    time_thresh = 10
    cur = 0
    cur = time_thresh
    alertMsg=""
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment=False)[0]

        # Apply NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres)
        t2 = time_synchronized()

        # Process detections
        


        for i, det in enumerate(pred):  # detections per image
            print("counter",counter)
            print("change",change)
            print("now",now)
            print("last",last)
            # print(test)
            # test-=1
            p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)
            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # img.jpg
            # txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
            txt_path = str(save_dir / 'labels' / p.stem) + (f'_{frame}' )  # img.txt
            s += '%gx%g ' % img.shape[2:]  # print string
            # print(len (det))
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            nHead = 0
            alert = 0
            if len(det): # number of people in frame
                # Rescale boxes from img_size to im0 size
                


                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                
                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                    
                # Write results
                for *xyxy, conf, cls in reversed(det):
                    # xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                    # line = (cls, *xywh, conf)
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4))).view(-1).tolist()
                    c = int(cls)  # integer class
                    xyxy2 = (torch.tensor(xyxy).view(1, 4)).view(-1).tolist()
                    line = (names[c], conf, *xyxy2)
                    with open(txt_path + '.txt', 'a') as f:
                        # f.write(('%g ' * len(line)).rstrip() % line + '\n')
                        f.write(('%s ' + '%g ' * (len(line)-1)).rstrip() % line + '\n')

                    label = f'{names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)
                    if(label.split()[0]=="head"):
                        nHead += 1
            else:
                with open(txt_path + '.txt', 'a') as f:
                    pass
            
            print(nHead)
            now = nHead
            if change:
                if  now>=last:
                    counter-=1
                else:
                    change = 0
                    counter = thresh        
            else:
                if  now>last:
                    change = 1
        
            if counter<0:
                cv2.imwrite(save_path, im0)

                timestr = "發現違規事件，時間："+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                img1 = open(save_path, 'rb')
                alertMsg={'time':timestr ,'img':img1}
                MakeAlert(alertMsg,1)
                cur = time_thresh
                change = 0
                counter = thresh
            
            cur-=1
            print("cur",cur)
            if cur==0:
                cur = time_thresh
                change = 0
                counter = thresh
                if nHead>0:
                    cv2.imwrite(save_path, im0)
                    timestr = "發現違規(定期檢查)時間："+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                    img1 = open(save_path, 'rb')
                    alertMsg={'time':timestr ,'img':img1}
                    counter = thresh
                    MakeAlert(alertMsg,1)
                    
                else:
                    cv2.imwrite(save_path, im0)
                    timestr = "確認安全(定期檢查)，時間："+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                    img1 = open(save_path, 'rb')
                    alertMsg={'time':timestr ,'img':None}
                    MakeAlert(alertMsg,0)



            last = now
            # if alert:
            #     MakeAlert(alertMsg)
            # Print time (inference + NMS)
            print(f'{s}Done. ({t2 - t1:.3f}s)')
            
            # Save results (image with detections)
            cv2.imshow("test",im0)
            print(f" The image with the result is saved in: {save_path}")

    print(f'Done. ({time.time() - t0:.3f}s)')
        
def detect(save_img=False):
    source, weights, view_img, save_txt, imgsz, trace = opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size, not opt.no_trace
    save_img = not opt.nosave and not source.endswith('.txt')  # save inference images
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))

    # Directories
    save_dir = Path(increment_path(Path(opt.project) / opt.name, exist_ok=opt.exist_ok))  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Initialize
    set_logging()
    device = select_device(opt.device)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size

    if trace:
        model = TracedModel(model, device, opt.img_size)

    if half:
        model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = check_imshow()
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz, stride=stride)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    # colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]
    colors = color_list()
    
    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    t0 = time.time()
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment=opt.augment)[0]

        # Apply NMS
        pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
        t2 = time_synchronized()

        # Apply Classifier
        if classify:
            pred = apply_classifier(pred, modelc, img, im0s)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
            else:
                p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # img.jpg
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
            s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if opt.save_conf else (cls, *xywh)  # label format
                        with open(txt_path + '.txt', 'a') as f:
                            f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    if save_img or view_img:  # Add bbox to image
                        label = f'{names[int(cls)]} {conf:.2f}'
                        plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)

            # Print time (inference + NMS)
            #print(f'{s}Done. ({t2 - t1:.3f}s)')

            # Stream results
            if view_img:
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                    print(f" The image with the result is saved in: {save_path}")
                else:  # 'video' or 'stream'
                    if vid_path != save_path:  # new video
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()  # release previous video writer
                        if vid_cap:  # video
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                            save_path += '.mp4'
                        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer.write(im0)

    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        #print(f"Results saved to {save_dir}{s}")

    print(f'Done. ({time.time() - t0:.3f}s)')


if __name__ == '__main__':
    
    MODEL_PATH = 'best.pt' #'runs/train/exp/weights/last.pt'
    IMAGE_PATH = 'images/test' #'../test_set/JPEGImages'
    DEVICE = 'cpu'
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=MODEL_PATH, help='model.pt path(s)')
    parser.add_argument('--source', type=str, default=IMAGE_PATH, help='source')  # file/folder, 0 for webcam
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--device', default=DEVICE, help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', default=False, help='display results')
    parser.add_argument('--save-txt', default=True, help='save results to *.txt')
    parser.add_argument('--save-conf', default=True, help='save confidences in --save-txt labels')
    parser.add_argument('--nosave', default=False, help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', default=True, help='existing project/name ok, do not increment')
    parser.add_argument('--no-trace', default=True, help='don`t trace model')
    opt = parser.parse_args()
    print(opt)
    #check_requirements(exclude=('pycocotools', 'thop'))

    source, weights, view_img, save_txt, imgsz, trace = opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size, not opt.no_trace
    
    with torch.no_grad():
        # while 1:
        if opt.update:  # update all models (to fix SourceChangeWarning)
            for opt.weights in ['yolov7.pt']:
                # detect()
                model = attempt_load(opt.weights, map_location=opt.device)
                detect2(opt.source, Path(opt.project) / opt.name, model, opt.device, opt.img_size, conf_thres = 0.55, iou_thres = 0.45)
                strip_optimizer(opt.weights)
        else:
            # detect()
            model = attempt_load(opt.weights, map_location=opt.device)
            detect2(opt.source, Path(opt.project) / opt.name, model, opt.device, opt.img_size, conf_thres = 0.55, iou_thres = 0.45)
        # time.sleep(3)
