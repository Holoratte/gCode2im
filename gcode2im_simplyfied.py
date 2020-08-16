#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      Holoratte
#
# Created:     16/08/2020
# Copyright:   (c) Holoratte 2020
# Licence:     <GPLv3>
#-------------------------------------------------------------------------------

import Tkinter, Tkconstants, tkFileDialog
import re
import PIL
from PIL import ImageDraw, Image, ImageOps
import math
import os
import g1tog23NoGui as g1tog23
import sys

def gcode2dict(filename):
    thisGcodeLine= {}
    gCodeDict =[]
    separator = '(M|G|X|Y|Z|I|J|K|F|S|P|;)'
    for line in open(filename,"rb"):
        thisGcodeLine= {}
        lineList = re.split(separator,line.rstrip('\n '))
        for i in range(len(lineList)):
            if lineList[i] == (";" or "(" or ""):
                break
            try:
                if lineList[i] in separator: thisGcodeLine[lineList[i]] = float(lineList[i+1].rstrip('\n '))
            except:
                pass
        gCodeDict.append(thisGcodeLine)
    return gCodeDict

def replace(filename, outputfilename, gCodeDict, GValue, axis, searchValue, newValue):
    posX, posY,posZ,i,j,k,g = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0
    a_list = ("M","G", "X", "Y", "Z", "I", "J", "K", "F", "S", "P")

    if searchValue == "*":

        for l in  gCodeDict:
            if l.get('G', None) != None:
                g = l.get('G')
                l["G"] = int(l.get("G"))
            if (l.get('G', None) == GValue) or (g == GValue) :
                l[axis]= newValue


        with open(outputfilename,"w") as f:

            for l in  gCodeDict:
                lsorted =[(key, l[key]) for key in a_list if key in l]
                for key, value in lsorted:
                    f.write(key + str(value) + " ")
                f.write("\n")



def dict2image(gCodeDict, draw):
    posX, posY,posZ,i,j,k,g = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0
    scaler = 1.0
    seqX = [x.get('X', 0) for x in gCodeDict]
    seqI = [x.get('I', 0) for x in gCodeDict]
    minX = min(seqX)
    maxX = max(seqX)
    seqY = [x.get('Y', 0) for x in gCodeDict]
    seqJ = [x.get('J', 0) for x in gCodeDict]
    minY = min(seqY)
    maxY = max(seqY)
    seqZ = [x.get('Z', 0) for x in gCodeDict]
    minZ = min(seqZ)
    maxZ = max(seqZ)
    offsetX = 0.0-minX
    offsetY = 0.0-minY
    offsetZ = 0.0-minZ
    dictScaler = ["X","Y","Z","I","J","K"]
    colorZ =0
    if maxX - minX == 0: maxX= 1e-200
    if maxY - minY == 0: maxY= 1e-200
    scaler = min(sizeX/(maxX - minX),sizeY/(maxY - minY))
    if maxZ-minZ == 0: scalerZcolor = 1
    elif maxZ-minZ > 0: scalerZcolor = 255/(minZ-maxZ)/scaler
    else: scalerZcolor = 255/(maxZ-minZ)/scaler
    print scalerZcolor, maxZ,minZ

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

        if l.get('X', None) != None or l.get('Y', None) != None or l.get('Z', None) != None or l.get('I', None) != None or l.get('J', None) != None or l.get('K', None) != None:
            if l.get('X', None) == None: l["X"]= posX
            if l.get('Y', None) == None: l["Y"]= posY
            if l.get('Z', None) == None: l["Z"]= posZ
            if l.get('I', None) == None: l["I"]= i
            if l.get('J', None) == None: l["J"]= j
            if l.get('K', None) == None: l["K"]= k
            if l.get('G', None) == None: l["G"]= g
            colorZ = int(l.get("Z")*scalerZcolor)
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
                if startAngle == stopAngle: stopAngle += 360
                radius = math.sqrt(l.get("I")**2+l.get("J")**2)
                draw.arc([centerX-radius, centerY-radius, centerX+radius, centerY+radius], startAngle, stopAngle, fill=colorZ, width=linewidth)
            elif l.get('G', None) == 2:
                centerX = posX+l.get("I") if l.get("I") != None else posX+i
                centerY = posY+l.get("J") if l.get("J") != None else posX+j
                if (posX-centerX) == 0:
                    centerX+=1e-200
                startAngle = math.degrees(math.atan2((posY-centerY),(posX-centerX)))
                if (l.get("X")-centerX) == 0:
                    centerX+=1e-200
                stopAngle = math.degrees(math.atan2((l.get("Y")-centerY),(l.get("X")-centerX)))
                if startAngle == stopAngle: stopAngle += 360
                if l.get("I") == None and l.get("J") != None:
                    radius = math.sqrt(i**2+l.get("J")**2)
                elif l.get("I") != None and l.get("J") == None:
                    radius = math.sqrt(l.get("I")**2+j**2)
                else:
                    radius = math.sqrt(l.get("I")**2+l.get("J")**2)
                draw.arc([centerX-radius, centerY-radius, centerX+radius, centerY+radius], stopAngle, startAngle, fill=colorZ, width=linewidth)
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
        filetypes = (("nc-Files",".nc .cnc"),("all files","*.*")));
    root.destroy()
    if filename != "":
        with open(filename, 'r') as file:
            input_line_count = sum(1 for line in file)
        print input_line_count
        linewidth = 1
        gdict = gcode2dict(filename)
        dict2image(gcode2dict(filename),draw)
        image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        image.show()
        filenameNoExt, file_extension = os.path.splitext(filename)
        filenamePNG = filenameNoExt + ".png"
        print filename
        image.save(filenamePNG)

        outputfilename = filenameNoExt + "_replaced" +".nc"
        replace(filename, outputfilename, gdict,1,"Z","*",-0.05)
        dict2image(gcode2dict(outputfilename),draw)
        image.show()

        SIMPLYFYGCODE = g1tog23.Gcode()
        SIMPLYFYGCODE.load(outputfilename,filenameNoExt +"_simplified" + ".nc" )
##        SIMPLYFYGCODE.load(filename,filenameNoExt +"_simplified" + ".nc" )

        image = Image.new(mode = "L", size = (sizeX, sizeY),color="white")
        draw = ImageDraw.Draw(image)
        dict2image(gcode2dict(filenameNoExt +"_simplified" + ".nc"),draw)
        image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        image.show()
        image.save(filenameNoExt +"_simplified" + ".png")


