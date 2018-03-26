# encoding=utf8 
import sys
 
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import re
import difflib
import time
from aip import AipOcr
import config

def main(videoname):
    conf = config.getConfig(videoname)

    APP_ID = conf['APP_ID']
    API_KEY = conf['API_KEY']
    SECRET_KEY = conf['SECRET_KEY']
    imgDir = conf['imgDir']
    outputDir = conf['outputDir']

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    def get_OCR(imgName):
        image = get_file_content(imgDir + '/' + imgName)

        options = {}
        options["recognize_granularity"] = "big"
        options["language_type"] = "CHN_ENG"
        options["detect_direction"] = "true"

        res = client.general(image, options)
        try:
            w = res['words_result']
            return w
        except:
            return False

    def is_img(f):
        return re.match(r'.+jpg', f);

    start = time.time()

    output = open(outputDir + str(start) + '.txt', 'a')

    pathDir = sorted(filter(is_img, os.listdir(imgDir)))

    positionData = [];
    for imgName in pathDir:
        output.write('Start: ' + imgName + '\n')
        ocrRes = get_OCR(imgName)
        # fail then retry
        while not(ocrRes):
            print 'Fail: ' + imgName
            ocrRes = get_OCR(imgName)
        for word in ocrRes:
            top = int(word['location']['top'])
            height = int(word['location']['height'])
            w = word['words']
            has = False
            for group in positionData:
                # belong to this group
                if abs(group['top'] - top) < (group['height'] / 2):
                    # Avoid duplicate: check if current word is similar to last word
                    lastWord = group['words'][len(group['words']) - 1]
                    if difflib.SequenceMatcher(None, lastWord, w).quick_ratio() > 0.8:
                        break
                    # append words
                    group['words'].append(w)
                    # cal new value
                    group['totalTop'] += top
                    group['totalHeight'] += height
                    group['totalNum'] += 1
                    group['top'] = group['totalTop'] / group['totalNum']
                    group['height'] = group['totalHeight'] / group['totalNum']
                    has = True
                    break

            if has == False:
                positionData.append({
                    'top': top,  # group standard, using average value of tops
                    'totalTop': top,
                    'height': height,
                    'totalHeight': height,
                    'totalNum': 1,  # how many pics has been add to this group 
                    'words': [w]
                });

            output.write('Words: ' + w + '\n')
            output.write('Top: ' + str(word['location']['top']) + '\n')
            output.write('Height: ' + str(word['location']['height']) + '\n')
        
        output.write('Finished: ' + imgName + '\n')
        print 'Finished: ' + imgName

    output.write(str(positionData) + '\n')

    max_group = []
    for group in positionData:
        if group['totalNum'] > len(max_group):
            max_group = group['words']
    allWords = ','.join(max_group)
    output.write('-----------------------' + '\n')
    output.write(allWords + '\n')
    output.write('-----------------------' + '\n')
    end = time.time()
    output.write('Running time: ' + str(end - start) + '\n')
    output.close()
    print 'Finished All'

# main()
