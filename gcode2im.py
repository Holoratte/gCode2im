#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      Holoratte
#
# Created:     08/03/2020
# Copyright:   (c) Holoratte 2020
# Licence:     <GPLv3>
#-------------------------------------------------------------------------------

import Tkinter, Tkconstants, tkFileDialog
import re
import PIL
from PIL import ImageDraw, Image, ImageOps
import math

def gcode2dict(filename):
    thisGcodeLine= {}
    gCodeDict =[]
    separator = '(M|G|X|Y|Z|I|J|K|F|S|P|;)'
    for line in open(filename,"rb"):
        thisGcodeLine= {}
        lineList = re.split(separator,line.rstrip('\n '))
        for i in range(len(lineList)):
            if lineList[i] == (";" or "("):
                break
            try:
                if lineList[i] in separator and lineList[i] != "" and lineList[i] != ";": thisGcodeLine[lineList[i]] = float(lineList[i+1].rstrip('\n '))
            except:
                pass
        gCodeDict.append(thisGcodeLine)
    return gCodeDict

def dict2image(gCodeDict, draw):

    posX, posY,posZ,i,j,k,g = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0
    scaler = 1.0
    seqX = [x.get('X', 0) for x in gCodeDict]
    minX = min(seqX)
    maxX = max(seqX)
    seqY = [x.get('Y', 0) for x in gCodeDict]
    minY = min(seqY)
    maxY = max(seqY)
    seqZ = [x.get('Z', 0) for x in gCodeDict]
    minZ = min(seqZ)
    maxZ = max(seqZ)
    offsetX = 0.0-minX
    offsetY = 0.0-minY
    offsetZ = 0.0-minZ
    dictScaler = ["X","Y","Z","I","J","K"]
    scaler = min(sizeX/(maxX - minX),sizeY/(maxY - minY))
    if maxZ-minZ == 0: scalerZcolor = 1
    else: scalerZcolor = 255/(maxZ-minZ)/scaler

    for l in  gCodeDict:
        for key, value in l.iteritems():
            if key =="X":
                l[key]= (value + offsetX)* scaler
            elif key =="Y":
                l[key]= (value + offsetY) * scaler
            elif key =="Z":
                l[key]= (value + offsetZ)* scaler
            elif key in dictScaler:
                l[key]= value * scaler

        if l.get('X', None) != None or l.get('Y', None) != None or l.get('Z', None) != None:
            if l.get('X', None) == None: l["X"]= posX
            if l.get('Y', None) == None: l["Y"]= posY
            if l.get('Z', None) == None: l["Z"]= posZ
            if l.get('G', None) == None: l["G"]= g
            colorZ = int(l.get("Z")*scalerZcolor if l.get("Z") else posZ*scalerZcolor)
    ##        print colorZ
            if l.get('G', None) == 1:
                draw.line([posX, posY,l.get('X'),l.get('Y')],fill=colorZ, width=linewidth)
            elif l.get('G', None) == 3:
                centerX = posX+l.get("I")
                centerY = posY+l.get("J")
                if (posX-centerX) == 0:
                    centerX+=1e-200
                if (posY-centerY) == 0:
                    centerY+=1e-200
                startAngle = math.degrees(math.atan2((posY-centerY),(posX-centerX)))
                if (l.get("X")-centerX) == 0:
                    centerX+=1e-200
                if (l.get("Y")-centerY) == 0:
                    centerY+=1e-200
                stopAngle = math.degrees(math.atan2((l.get("Y")-centerY),(l.get("X")-centerX)))
                radius = math.sqrt(l.get("I")**2+l.get("J")**2)
                draw.arc([centerX-radius, centerY-radius, centerX+radius, centerY+radius], startAngle, stopAngle, fill=colorZ, width=linewidth)
            elif l.get('G', None) == 2:
                centerX = posX+l.get("I")
                centerY = posY+l.get("J")
                if (posX-centerX) == 0:
                    centerX+=1e-200
                startAngle = math.degrees(math.atan2((posY-centerY),(posX-centerX)))
                if (l.get("X")-centerX) == 0:
                    centerX+=1e-200
                stopAngle = math.degrees(math.atan2((l.get("Y")-centerY),(l.get("X")-centerX)))
                radius = math.sqrt(l.get("I")**2+l.get("J")**2)
                draw.arc([centerX-radius, centerY-radius, centerX+radius, centerY+radius], stopAngle, startAngle, fill=colorZ, width=linewidth)
    ##        else: print l
            if l.get('X', None) != None: posX = l.get('X')
            if l.get('Y', None) != None: posY = l.get('Y')
            if l.get('Z', None) != None: posZ = l.get('Z')
            if l.get('I', None) != None: i= l.get("I")
            if l.get('J', None) != None: j= l.get("J")
            if l.get('K', None) != None: k= l.get("K")
            if l.get('G', None) != None: g = l.get('G')

##    return image
if __name__ == '__main__':
    sizeX = 7000
    sizeY = 4000
    image = Image.new(mode = "L", size = (sizeX, sizeY),color="white")
    draw = ImageDraw.Draw(image)

    root = Tkinter.Tk()
    root.withdraw()
    filename = ""
    filename = tkFileDialog.askopenfilename(initialdir = "./",title = "Select file",
        filetypes = (("nc-Files","*.nc"),("all files","*.*")));
    root.destroy()
    if filename != "":
        linewidth = 1
        dict2image(gcode2dict(filename),draw)
        image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        image.show()
