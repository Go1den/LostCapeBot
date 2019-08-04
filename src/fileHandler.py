def writeToFile(file, mode, message):
    try:
        with open(file, mode) as myfile:
            myfile.write(message)
    except:
        print("Failed to write to file " + file)
