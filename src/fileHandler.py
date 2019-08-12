def writeToFile(file, message):
    try:
        with open(file, 'w') as myfile:
            myfile.write(message)
    except:
        print("Failed to write to file " + file)
