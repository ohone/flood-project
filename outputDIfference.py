import shapely
import fiona
import math
import decimal
import glob
import csv
import numpy as np
from shapely.geometry import Point

file_list0 = glob.glob('./csvdir1/*.csv')
file_list1 = glob.glob('./csvdir2/*.csv')


def sameCoords(rowA, rowB):
    if rowA is None or rowB is None:
        False
    elif rowA["XCen"] == rowB["XCen"] and rowA["YCen"] == rowB["YCen"]:
        True
    else:
        False


def existsGeologyDifference(file_list0, file_list1):
    file0 = file_list0[0]
    file1 = file_list1[0]
    with open(file0) as File0, open(file1) as File1:
        readerI = csv.DictReader(File0)
        readerJ = csv.DictReader(File1)
        for rowI, rowJ in zip(readerI, readerJ):
            # if sync is broken (due to building removals/addition)
            if sameCoords(rowI, rowJ) is False:
                return true
        return False


def addToData(rowI, rowJ, points, velocities, depthValues):
    if rowI is None:
        addToData({'XCen': rowJ["XCen"], 'YCen': rowJ["YCen"], 'Vx': rowJ["Vx"], 'Vy': rowJ["Vy"], 'Depth': rowJ["Depth"]},
                  rowJ, points, velocities, depthValues)
    if rowJ is None:
        points.append(Point(float(rowI["XCen"]), float(rowI["YCen"])))
        velocities.append([-9999, -9999])
        depthValues.append([-9999])
    else:
        points.append(Point(float(rowI["XCen"]), float(rowI["YCen"])))
        Vx = (float(rowI["Vx"])) - (float(rowJ["Vx"]))
        Vy = (float(rowI["Vy"])) - (float(rowJ["Vy"]))

        #Vx = (float(rowJ["Vx"])) - (float(rowI["Vx"]))
        #Vy = (float(rowJ["Vy"])) - (float(rowI["Vy"]))
        velocities.append([Vx, Vy])
        depthValues.append(float(rowI["Depth"]) - (float(rowJ["Depth"])))


def returnsRowsInOrder(rowA, rowB):
    if rowA["XCen"] > rowB["XCen"]:
        return [rowA, rowB]
    elif rowB["XCen"] > rowA["XCen"]:
        return [rowB, rowA]
    elif rowA["YCen"] > rowB["YCen"]:
        return [rowA, rowB]
    elif rowA["YCen"] < rowB["YCen"]:
        return [rowB, rowA]
    else:
        return [rowA, rowB]


def creategrid(points, values, dimensionsDict):
    print "Processing Data..."
    # create empty array with zeros
    data = np.zeros((dimensionsDict["Cols"], dimensionsDict["Rows"]))
    data.fill(-9999)
    for i in range(len(points)):
        point = points[i]
        data[((point.x - dimensionsDict["minX"]) / 2) - 1,
             ((point.y - dimensionsDict["minY"]) / 2) - 1] = values[i]
    return data


def writeasciigrid(filename,  values, dimensionsDict, gridsize, nullvalue=-9999):
    "Writing ASCII Grid..."
    cols = dimensionsDict["Cols"]
    rows = dimensionsDict["Rows"]
    startx = dimensionsDict["minX"]
    starty = dimensionsDict["minY"]
    header = "ncols {0}\n".format(cols)
    header += "nrows    {0}\n".format(rows)
    header += "xllcorner {0}\n".format(startx)
    header += "yllcorner {0}\n".format(starty)
    header += "cellsize {0}\n".format(gridsize)
    header += "NODATA_value {0}\n".format(nullvalue)
    with open(filename, "w") as f:
        f.write(header)
        for i in range(0, values.shape[1]):
            for j in range(0, values.shape[0]):
                f.write(str(values[j, i]))
                f.write('\t')
            f.write('\n')
    return True


def importsCSVs(file_list0, file_list1):
    print "Importing Data..."
    pointsList = []
    velocitiesList = []
    depthValuesList = []
    for i, j in zip(file_list0, file_list1):
        with open(i) as iFile, open(j) as jFile:
            readerI = csv.DictReader(iFile)
            readerJ = csv.DictReader(jFile)
            bufferedRowJ = None
            bufferedRowI = None
            points = []
            velocities = []
            depthValues = []
            for rowI, rowJ in zip(readerI, readerJ):
                # if sync is broken (due to building removals/addition)
                if sameCoords(rowI, rowJ) is False:
                    # if the change is in the 'after' file
                    if returnsRowsInOrder(rowI, rowJ)[0] == rowI:
                        if bufferedRowJ:  # if buffered point exists
                            if sameCoords(rowI, bufferedRowJ):  # if buffered point matches
                                addToData(rowI, bufferedRowJ, points,
                                          velocities, depthValues)
                                bufferedRowJ = rowJ

                            elif returnsRowsInOrder(rowI, bufferedRowJ)[0] == bufferedRowJ:
                                addToData(None, bufferedRowJ, points,
                                          velocities, depthValues)
                                addToData(rowI, None, points,
                                          velocities, depthValues)
                                bufferedRowJ = None
                        else:
                            addToData(rowI, None, points,
                                      velocities, depthValues)
                            bufferedRowJ = rowJ
                    else:
                        if bufferedRowI:
                            if sameCoords(rowJ, bufferedRowI):
                                addToData(rowJ, bufferedRowI, points,
                                          velocities, depthValues)
                            elif returnsRowsInOrder(rowJ, bufferedRowI)[0] == bufferedRowI:
                                addToData(bufferedRowI, None, points,
                                          velocities, depthValues)
                                addToData(None, rowJ, points,
                                          vleocities, depthValues)
                            bufferedRowI = rowI
                        else:  # if there is no buffer value
                            addToData(None, rowJ, points,
                                      velocities, depthValues)
                            bufferedRowI = row

                else:
                    if bufferedRowJ:
                        addToData(None, bufferedRowJ, points,
                                  velocities, depthValues)
                        bufferedRowJ = None
                    addToData(rowI, rowJ, points, velocities, depthValues)

        pointsList.append(points)
        velocitiesList.append(velocities)
        depthValuesList.append(depthValues)
    return pointsList, velocitiesList, depthValuesList


def getDimensions(pointsList):
    minX = 100**10
    maxX = 0
    minY = 100**10
    maxY = 0
    for point in pointsList[0]:
        if point.x < minX:
            minX = point.x
        if point.x > maxX:
            maxX = point.x
        if point.y < minY:
            minY = point.y
        if point.y > maxY:
            maxY = point.y

    Cols = (maxX - minX) / 2
    Rows = (maxY - minY) / 2
    return {"minX": minX, "maxX": maxX, "minY": minY, "maxY": maxY, "Cols": Cols, "Rows": Rows}


def produceCSV(pointsList, velocitiesList, depthValuesList):
    count = 0
    for points, velocities, depthValues in zip(pointsList, velocitiesList, depthValuesList):
        with open("csvOUTPUTdir/outfile{}".format(count) + '.csv', 'wb') as fout:
            fieldnames = ['XCen', 'YCen', 'Depth', 'Vx', 'Vy']
            o = csv.DictWriter(fout, fieldnames)
            o.writeheader()
            for point, velocity, depthVal in zip(points, velocities, depthValues):
                o.writerow({'XCen': point.x, 'YCen': point.y,
                            'Depth': depthVal, 'Vx': velocity[0], 'Vy': velocity[1]})
        count = count + 1


pointsList, velocitiesList, depthValuesList = importsCSVs(
    file_list0, file_list1)
dimensionsDictionary = getDimensions(pointsList)


def modVelocitiesList(velocities):
    absVelList = []
    for x in velocities:
        if x[0] != -9999:
            absVelList.append(math.sqrt((x[0] ** 2) + (x[1] ** 2)))
        else:
            absVelList.append(-9999)
    return absVelList


if (existsGeologyDifference(file_list0, file_list1) is True):  # false for testing purposes
    pointsList, velocitiesList, depthValuesList = importsCSVs(file_list0, file_list1)
    produceCSV(pointsList, velocitiesList, depthValuesList)
    for i in range(len(pointsList)):
        data = creategrid(pointsList[i], modVelocitiesList(velocitiesList[i]), dimensionsDictionary)
        writeasciigrid("ASCIIout/outfile{}".format(i) + '.asc', data, dimensionsDictionary, 2, -9999)
    print "Output generated."
else:
    print "No difference in geology, so no output difference expected or produced."
