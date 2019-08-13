import textwrap

def validate(levelCode):
    if len(levelCode) == 9 and levelCode.isalnum():
        return True
    else:
        print("Invalid level code! " + levelCode)
        return False

def pad(levelCode):
    segmentsOfLevelCode = textwrap.wrap(levelCode, 3)
    print("Level code: " + '-'.join(segmentsOfLevelCode))
    return '-'.join(segmentsOfLevelCode).upper()
