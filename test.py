#!/usr/bin/python
#coding=utf-8
import sys, getopt
import os
import pathlib
import re

supportedFileType = {
}

tobeAnalizedFileType = [
    ".png", ".jpg"
]

tobeAnalizedFileDictionary = {
}

def recursiveDirFileList(path):
    list = [x for x in path.iterdir()]
    dirList = []
    fileList = []
    for val in list:
        if val.is_dir():
            dirList.append(val)
        elif val.is_file():
            fileList.append(val)
    for val in dirList:
        subFileList = recursiveDirFileList(val)
        if not subFileList is None:
            fileList += subFileList
    return fileList

def isOCStringLiteral(string):
    return re.match("^@\".*\"$", string) is not None

def sourceFileAnalizer(file):
    m = re.findall('(?<=\[UIImage imageNamed:).*?(?=\])', file)
    if m is not None:
        for imageName in m:
            if isOCStringLiteral(imageName):
                print("this is a string literal" + imageName)
                pass
    return

def xibFileAnalizer(file):
    # print(path)
    return

def setupSupportedFile():
    supportedFileType[".m"] = sourceFileAnalizer
    supportedFileType[".mm"] = sourceFileAnalizer
    supportedFileType[".cpp"] = sourceFileAnalizer
    supportedFileType[".xib"] = xibFileAnalizer
    return

def main(argv):
    workingDir = pathlib.Path.cwd()
    try:
        opts, args = getopt.getopt(argv, None)
        if len(args) > 0:
            workingDir = args[0]
            pass
        pass
    except getopt.GetoptError:
        print("Error")
        raise e
    path = pathlib.Path(os.path.expanduser(workingDir))
    if not path.exists():
        print("Illegel working path %s" % path)
        return
    setupSupportedFile()
    files = recursiveDirFileList(path)
    for filepath in files:
        if len(filepath.suffixes) > 0:
            suffix = filepath.suffix
            if suffix in tobeAnalizedFileType:
                tobeAnalizedFileDictionary[filepath.name] = 0
                pass

            if suffix in supportedFileType:
                f = open(filepath.as_posix(), 'r')
                file = f.read()
                f.close()
                supportedFileType[suffix](file)
                pass

    return

if __name__ == "__main__":
    main(sys.argv[1:])

