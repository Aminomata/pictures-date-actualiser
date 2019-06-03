import os
from stat import ST_ATIME
from stat import ST_MTIME
from tkinter import Tk
from tkinter import filedialog
from PIL import Image
import time
import datetime
import shutil
import pywintypes
import win32file
import win32con
import _thread
from threading import Thread, Lock, Condition

newtime = None


def chooseFileName():
    root = Tk()
    root.withdraw()
    root.filename = filedialog.askdirectory()
    dName = root.filename
    print('Folder name: ' + dName + '\n--------------')
    root.destroy()
    return dName


def changeTime(f, i, today):
    s = os.stat(f)
    atime = s[ST_ATIME]
    # print('Creation date: ' + str(atime))
    mtime = s[ST_MTIME]
    # print('Modify date: ' + str(mtime))

    format = "%a %b %d %H:%M:%S %Y"
    global newtime

    s = today.strftime(format)
    # print(s)

    tntime = (newtime + datetime.timedelta(seconds=i)).timestamp()
    # print('New date: ' + str(tntime))
    # print(tntime)
    os.utime(f, (tntime, tntime))
    # print('--------------')


def changeCreationTime(f):
    wintime = datetime.datetime.today()
    winfile = win32file.CreateFile(
        f, win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None, win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL, None)
    win32file.SetFileTime(winfile, wintime)
    winfile.close()


def deleteEXIFData(f):
    image_file = open(f, 'rb')
    image = Image.open(image_file)
    image.save(f + '.png')
    return f + '.png'


def changeDate(fileList, i, dFolder, dName, folder, fileCounter):
    filename = fileList[i]
    # print('File name: ' + filename)
    f = dFolder + '/' + filename
    shutil.copy(f, dName + '/backup/' + folder + '/' + filename)
    changeCreationTime(f)
    f = deleteEXIFData(f)
    changeTime(f, i, newtime)
    shutil.move(f, dName + '/sorted' + '/' +
                filename + '-' + ('%04d' % (fileCounter + i)) + '.png')


def main():
    today = datetime.datetime.today()
    global newtime
    newtime = today
    while (1):
        t1 = time.time()
        dName = chooseFileName()
        if not os.path.exists(dName + '/sorted'):
            os.makedirs(dName + '/sorted')
        if not os.path.exists(dName + '/backup'):
            os.makedirs(dName + '/backup')

        fileCounter = 0
        folderList = os.listdir(dName)
        numberOfFolders = len(folderList)
        skipped_folders = 0
        for j in range(0, numberOfFolders):
            folder = folderList[j]
            if (folder == "sorted" or folder == "backup"):
                skipped_folders += 1
                numberOfFolders -= 1
                continue
            dFolder = dName + '/' + folder
            if not os.path.exists(dName + '/backup/' + folder):
                os.makedirs(dName + '/backup/' + folder)

            fileList = os.listdir(dFolder)
            numberOfFiles = len(fileList)
            threads = []
            for i in range(0, numberOfFiles):
                thread = Thread(target=changeDate, args=(
                    fileList, i, dFolder, dName, folder, fileCounter))
                thread.start()
                threads.append(thread)

            for t in threads:
               t.join()
            fileCounter += numberOfFiles
            newtime = newtime + datetime.timedelta(seconds=numberOfFiles)
            print(f"Folder {j + 1 - skipped_folders}/{numberOfFolders}")


        t2 = time.time()
        print(f"Took {t2 - t1} seconds")
        input("Press to choose again..")


main()
