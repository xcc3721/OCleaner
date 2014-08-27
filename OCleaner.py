#!/usr/bin/python
#coding=utf-8
import sys, getopt
import os
import pathlib
import re

tobeAnalizedFileType = [
    ".png", ".jpg"
]

tobeAnalizedFileDictionary = {
}

AnalizeFileInstance = []

class AnalizeManager:
    def supportedFileTypes():
        ret = []
        for analizer in AnalizeFileInstance:
            ret = ret + analizer.fileTypes
        return ret
    def registeAnalizer(analizer):
        AnalizeFileInstance.append(analizer)

class AnalizeFile:
    def __init__(self):
        self.fileTypes = None
        self.regexes = None
    def analize(self, file):
        pass

class SourceAnalizeFile(AnalizeFile):
    def __init__(self):
        self.fileTypes = ['.m', '.cpp']
        self.regexes = [
            '(?<=\[UIImage imageNamed:).*?(?=\])',
            '(?<=myInitImage:).*?(?=)',
            '@".*?"'
        ]

    def analize(self, file):
        i = 0
        for reg in self.regexes:
            m = re.findall(reg, file)
            if m is not None:
                for imageName in m:
                    literalMatch = OCStringLiteral(imageName)
                    if literalMatch is not None:
                        possibleNames = possibleImageFileNames(literalMatch)
                        for candidateImageName in possibleNames:
                            if candidateImageName in tobeAnalizedFileDictionary:
                                tobeAnalizedFileDictionary[candidateImageName] += 1
                    else:
                        print("Need Manual Check:%s" % imageName)
            i += 1


class XibSourceAnalizeFile(AnalizeFile):
    def __init__(self):
        self.fileTypes = ['.xib']
        self.regexes = [
        '(?<=<string key="NSResourceName">).*(?=</string>)',
        '(?<=<image name=").*?(?=")',
        '(?<=image=").*?(?=")'
        ]

    def analize(self, file):
        for reg in self.regexes:
            m = re.findall(reg, file)
            if m is not None:
                for imageName in m:
                    possibleNames = possibleImageFileNames(imageName)
                    for imageName in possibleNames:
                        if imageName in tobeAnalizedFileDictionary:
                            tobeAnalizedFileDictionary[imageName] += 1



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

def OCStringLiteral(string):
    match = re.search("(?<=^@\").*(?=\"$)", string)
    if match is not None:
        return match.group()
    return  None

def possibleImageFileNames(imageName):
    path = pathlib.Path(imageName)
    stem = path.stem
    suffixes = path.suffixes
    if len(suffixes) == 0:
        suffixes = tobeAnalizedFileType
    scaleIdx = stem.find("@2x")
    shortImageName = None
    if scaleIdx >= 0:
        shortImageName = stem[:scaleIdx]
    else:
        shortImageName = stem
    if len(shortImageName) == 0:
        return ()
    else:
        ret = []
        for suffix in suffixes:
            ret.append(shortImageName+suffix)
            ret.append(shortImageName+"@2x"+suffix)
        return tuple(ret)


def setupSupportedFile():
    AnalizeManager.registeAnalizer(SourceAnalizeFile())
    AnalizeManager.registeAnalizer(XibSourceAnalizeFile())
    return

def noneUsedResourceList():
    ret = []
    for k in tobeAnalizedFileDictionary:
        v = tobeAnalizedFileDictionary[k]
        if v <= 0:
            ret.append(k)
    return ret

def usedResourceDictionary():
    ret = {}
    for k in tobeAnalizedFileDictionary:
        v = tobeAnalizedFileDictionary[k]
        if v > 0:
            ret[k] = v
    return ret

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

    for filepath in files:
        if len(filepath.suffixes) > 0:
            suffix = filepath.suffix
            if suffix in AnalizeManager.supportedFileTypes():
                f = open(filepath.as_posix(), 'r')
                file = f.read()
                f.close()
                for analizer in AnalizeFileInstance:
                    if suffix in analizer.fileTypes:
                        analizer.analize(file)

    print("All Resources:%d" % len(tobeAnalizedFileDictionary))
    print("None Used:%d" % len(noneUsedResourceList()))
    print("Used:%d" % len(usedResourceDictionary()))
    print("---------------------------------------------")
    # print("Used Detail:%s" %  usedResourceDictionary())
    for unUsed in sorted(noneUsedResourceList(), key=str.lower):
        print("%s" % unUsed)


    return

if __name__ == "__main__":
    main(sys.argv[1:])

