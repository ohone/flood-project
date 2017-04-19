import shapely
import fiona
import math
from numpy import *
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import shape

resolution = 10
#how many rows/columns the shapefile is split into

diff = fiona.open('difference/difference.shp')
initial = fiona.open('shapefile/buildings.shp')

Xincriment = (initial.bounds[2] - initial.bounds[0])/resolution
Yincriment = (initial.bounds[3] - initial.bounds[1])/resolution

def getPolygonList (shapefile):
    myList = []
    for feature in shapefile:
        try:
            myList.append(shape(feature['geometry']))
        except:
            pass
    return myList

def getTotalArea (shapefile):
    print "computing area..."
    myList = getPolygonList(shapefile)
    totalArea = 0.0
    for shape in myList:
        totalArea = totalArea + shape.area
    return totalArea

def getSD (shapefile):
    myList = getPolygonList (shapefile)
    average = len(myList)/resolution ** 2
    newList = [[0 for x in range(2)] for y in range(resolution ** 2)]
    spread = 0.0
    weights = 0.0
    weightsList = []
    for shape in myList:
        weights = weights + shape.area
        x = shape.centroid.x - initial.bounds[0]
        y = shape.centroid.y - initial.bounds[1]
        x = int(x / Xincriment)
        y = int(y / Yincriment)
        newList[y * resolution + x][0] = newList[y * resolution + x][0] + 1
        newList[y * resolution + x][1] = newList[y * resolution + x][1] + shape.area

    numberOfNonZero = 0
    cellsum = 0.0
    for cell in newList:
        cellsum = cellsum + (cell[0]*cell[1])
        if cell[1] != 0:
            numberOfNonZero = numberOfNonZero + 1

    weightedMean = cellsum/weights

    #weighted variance
    numerator = 0.0
    for cell in newList:
        numerator = numerator + (cell[1]*((cell[0] - weightedMean) ** 2))
    denominator = ((numberOfNonZero - 1) * weights)/numberOfNonZero
    weightedVariance = numerator/denominator

    SD = math.sqrt(weightedVariance)

    return SD


initialArea = getTotalArea(initial)
differenceArea = getTotalArea(diff)
percentageChangeInArea = (differenceArea/initialArea * 100)

print "Percentage change in area: ", percentageChangeInArea
print "standard deviation: ", getSD(diff)
