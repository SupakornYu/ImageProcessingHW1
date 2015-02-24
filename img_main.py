import wx
"""import ImageTk"""
import numpy as np
import matplotlib.pyplot as plt
import math

class Panel1(wx.Panel):
    """class Panel1 creates a panel with an image on it, inherits wx.Panel"""
    def __init__(self, parent, id):
        # create the panel
        wx.Panel.__init__(self, parent, id)
        try:
            # pick an image file you have in the working folder
            # you can load .jpg  .png  .bmp  or .gif files
            image_file = 'scaled_shapes.pgm'
            bmp1 = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            # image's upper left corner anchors at panel coordinates (0, 0)
            self.bitmap1 = wx.StaticBitmap(self, -1, bmp1, (0, 0))
            # show some image details
            str1 = "%s  %dx%d" % (image_file, bmp1.GetWidth(), bmp1.GetHeight())
            parent.SetTitle(str1)
        except IOError:
            print "Image file %s not found" % imageFile
            raise SystemExit

        # button goes on the image --> self.bitmap1 is the parent
        self.button1 = wx.Button(self.bitmap1, id=-1, label='Button1', pos=(8, 8))


class ImageLib:
    def readPGMImage(self,path):
        file = open(path, "rb")
        pgmVer = file.readline().split()
        pgmComment = []
        while True:
            pgmComment_eachline = file.readline()
            if(pgmComment_eachline[0]=="#"):
                pgmComment.append(pgmComment_eachline)
            else:
                break
        pgmSize = pgmComment_eachline.split()
        pgmGreyscale = file.readline().split()
        pgmDataList = []
        htg = np.zeros((256),dtype=np.int32)
        np.set_printoptions(suppress=True)
        for j in range(int(pgmSize[1])):
            pgmDataX = []
            for i in range(int(pgmSize[0])):
                byte = file.read(1)
                chrToInt = ord(byte)
                pgmDataX.append(chrToInt)
                htg[chrToInt] = htg[chrToInt]+1
            pgmDataList.append(pgmDataX)
        file.close()
        pgmData = np.asarray(pgmDataList,dtype=np.int32)
        return pgmVer,pgmComment,pgmSize,pgmGreyscale,pgmData,htg
        #pgmData is data pixel that i get from pgm file under grey level value(numpy array).
        #pgmSize contain width and height of pixel(list).
        #htg is a histogram of image (numpy array).

    def plotHistogramFromArray(self,histogram_arr):
        index = np.arange(256)
        bar_width = 0.35
        opacity = 0.4
        rects1 = plt.bar(index, histogram_arr, bar_width,
                         alpha=opacity,
                         color='b',
                         label='histogram1')
        plt.xlabel('Grey level')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def countingObject(self,histogram,threshold_object):
        countObject = 0
        countObjectGreyLevel = []
        for i in range(histogram.size):
            if histogram[i] >= threshold_object:
                countObject += 1
                countObjectGreyLevel.append(i)
        countObjectGreyLevel.remove(max(countObjectGreyLevel))
        return countObject-1,countObjectGreyLevel # minus 1 for backgroud

    def pqMoment(self,p,q,pqmData,pgmSize,greyLevel,greyLevelSelected):
        moment = 0
        pgmDataMoment = np.zeros((int(pgmSize[1]),int(pgmSize[0])), dtype=np.int32)
        for i in range(int(pgmSize[1])):
            for j in range(int(pgmSize[0])):
                if pgmData[i][j] == greyLevelSelected:
                    pgmDataMoment[i][j] = 1
                else:
                    pgmDataMoment[i][j] = 0
                moment += ((math.pow(j,p))*((math.pow(i,q))*pgmDataMoment[i][j]))
        #ImageLib.buildPGMFile(self,"testmoment",pgmSize[0],pgmSize[1],greyLevel,pgmDataMoment)
        return moment,pgmDataMoment

    def centralMoment(self,p,q,pgmData,pgmSize,greyLevel,greyLevelSelected):
        centralMoment = 0
        moment1,pgmDataMoment = ImageLib.pqMoment(self,1,0,pgmData,pgmSize,greyLevel,greyLevelSelected)
        moment2,pgmDataMoment = ImageLib.pqMoment(self,0,1,pgmData,pgmSize,greyLevel,greyLevelSelected)
        moment3,pgmDataMoment = ImageLib.pqMoment(self,0,0,pgmData,pgmSize,greyLevel,greyLevelSelected)
        xCoor = moment1/moment3
        yCoor = moment2/moment3
        for i in range(int(pgmSize[1])):
            for j in range(int(pgmSize[0])):
                centralMoment += ((math.pow((j-xCoor),p))*((math.pow(i-yCoor,q))*pgmDataMoment[i][j]))
        return centralMoment

    def scaleInvariantMoment(self,p,q,pgmData,pgmSize,greyLevel,greyLevelSelected):
        scaleInvariantMoment = 0
        centralMomentPQ = ImageLib.centralMoment(self,p,q,pgmData,pgmSize,greyLevel,greyLevelSelected)
        centralMoment00 = ImageLib.centralMoment(self,0,0,pgmData,pgmSize,greyLevel,greyLevelSelected)
        scaleInvariantMoment = centralMomentPQ/(math.pow(centralMoment00,(1+((p+q)/2))))
        return scaleInvariantMoment

    def buildPGMFile(self,fileName,width,height,greyLevel,pgmData):
        f = open(str(fileName)+".pgm","wb")
        f.write("P5\n");
        f.write("# "+str(fileName)+"\n");
        f.write(str(width)+" "+str(height)+"\n"+str(greyLevel[0])+"\n");
        for i in range(int(height)):
            for j in range(int(width)):
                if pgmData[i][j]<0:
                    pgmData[i][j] = 0
                elif pgmData[i][j]>int(greyLevel[0]):
                    pgmData[i][j] = int(greyLevel[0])
                f.write(chr(pgmData[i][j]));
        f.close()

    def histogramEqualization(self,outputFileName,inputFileName):
        pgmVer,pgmComment,pgmSize,pgmGreyscale,pgmData,htg = ImageLib.readPGMImage(self,str(inputFileName)+".pgm")
        imgArea = int(pgmSize[0])*int(pgmSize[1])
        htgScaleAfter = np.zeros(int(pgmGreyscale[0])+1,dtype=np.int32)
        propOfA = 0.0
        for i in range(htg.size):
            propOfA += float(htg[i])/float(imgArea)
            #print "propA" + str(propOfA)
            fDa = propOfA * float(pgmGreyscale[0])
            htgScaleAfter[i] = round(fDa)
        pgmDataAfter = np.zeros((int(pgmSize[1]),int(pgmSize[0])),dtype=np.int32)
        for i in range(int(pgmSize[1])):
            for j in range(int(pgmSize[0])):
                pgmDataAfter[i][j] = htgScaleAfter[pgmData[i][j]]
        ImageLib.buildPGMFile(self,outputFileName,pgmSize[0],pgmSize[1],pgmGreyscale,pgmDataAfter)

    def geometricOperationsImage(self,redPgmFileName,greenPgmFileName,bluePgmFileName):
        redpgmVer,redpgmComment,redpgmSize,redpgmGreyscale,redpgmData,redhtg = ImageLib.readPGMImage(self,str(redPgmFileName)+".pgm")
        greenpgmVer,greenpgmComment,greenpgmSize,greenpgmGreyscale,greenpgmData,greenhtg = ImageLib.readPGMImage(self,str(greenPgmFileName)+".pgm")
        bluepgmVer,bluepgmComment,bluepgmSize,bluepgmGreyscale,bluepgmData,bluehtg = ImageLib.readPGMImage(self,str(bluePgmFileName)+".pgm")

        print redpgmData
        print greenpgmData
        print bluepgmData

        geo1 = ((2*redpgmData)-greenpgmData)-bluepgmData
        ImageLib.buildPGMFile(self,"geo1",redpgmSize[0],redpgmSize[1],redpgmGreyscale,geo1)

        geo2 = (redpgmData-bluepgmData)
        ImageLib.buildPGMFile(self,"geo2",redpgmSize[0],redpgmSize[1],redpgmGreyscale,geo2)

        geo3 = (redpgmData+greenpgmData+bluepgmData)/3
        ImageLib.buildPGMFile(self,"geo3",redpgmSize[0],redpgmSize[1],redpgmGreyscale,geo3)

"""
#3
myLib = ImageLib()
myLib.geometricOperationsImage("SanFranPeak_red","SanFranPeak_green","SanFranPeak_blue")
"""

"""
#2
myLib = ImageLib()
myLib.histogramEqualization("EqualCameraman","Cameraman")
myLib.histogramEqualization("EqualSEM256_256","SEM256_256")
"""



"""
#1.1
myLib = ImageLib()
pgmVer,pgmComment,pgmSize,pgmGreyscale,pgmData,htg = myLib.readPGMImage('scaled_shapes.pgm')
#myLib.buildPGMFile("test",pgmSize[0],pgmSize[1],pgmGreyscale,pgmData)
print htg
#monent,pgmDataMoment =  myLib.pqMoment(1,1,pgmData,pgmSize,pgmGreyscale,255)
print "object : "+ str(myLib.countingObject(htg,1000))
myLib.plotHistogramFromArray(htg)
"""

"""
#1.2
print myLib.centralMoment(2,0,pgmData,pgmSize,pgmGreyscale,80)
print myLib.scaleInvariantMoment(2,0,pgmData,pgmSize,pgmGreyscale,80)+myLib.scaleInvariantMoment(0,2,pgmData,pgmSize,pgmGreyscale,80)
"""


"""
pgmVer,pgmComment,pgmSize,pgmGreyscale,pgmData,htg = myLib.readPGMImage('scaled_shapes.pgm')
#print ImageLib().pqMoment(1,1,pgmData,pgmSize)
print pgmData
print pgmSize
print htg
myLib.plotHistogramFromArray(htg)

"""

app = wx.App()
# create a window/frame, no parent, -1 is default ID
# change the size of the frame to fit the backgound images
frame1 = wx.Frame(None, -1, "An image on a panel", size=(600, 500))
# create the class instance
panel1 = Panel1(frame1, -1)
frame1.Show(True)
app.MainLoop()


