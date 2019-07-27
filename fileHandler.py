def writeToFile(file, mode, message):
    with open(file, mode) as myfile:
        myfile.write(message)
