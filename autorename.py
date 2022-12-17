#!/usr/bin/env python3

import os
import platform
import sys
import re
import glob

#List of words to be changed to lowercase
wordsToLower = ["The", "A", "An", "And", "Und", "But", "Or", "Nor", "At", "By", "For", "From", 
                "In", "Into", "Of", "Off", "On", "Onto", "Out", "Over", "To", "Up", "With", "As", 
                "Fra", "Et", "Ov",]
                #NOTE: The word "as" should be capitalized if it's followed by a verb. This app warns the user but does not have the ability to detect verbs.

#Regular expressions used to process filenames
regex = None

def main():

    global regex
    changesPending = False
    oldFilenames = []
    newFilenames = []

    #Get regular expressions and process the user-specified, command-line arguments
    regex = Regex()
    args = getCommandLineArguments()

    #---------------------------------------------------------#
    # Process Every Filename and Create a New Filename String #
    #---------------------------------------------------------#
    for filename in glob.glob('*' + args.targetFileType):

        fileRenamed = False
        caseChanged = False
        filenameContainsTheWordAs = False
        newFilename = filename
        extension = os.path.splitext(filename)[1]
        separatorPosInNumber = 0 #Position of separator if part of the starting number: Assume it's not
        wordPosition = 0
        numLength = 0

        #--------------------------------------#
        # Split Filename Into Individual Words #
        #--------------------------------------#

        #Get starting number and set starting position of title
        numMatch = regex.numPattern.match(filename)
        if numMatch: #Check for starting number in filename
            num = numMatch.group()
            numLength = numMatch.end()
            #Check if starting number was split into its own word
            if len(newFilename) > numLength and newFilename[numLength] == args.filenameDelimiter:
                wordPosition += 1 #Add one to skip starting number when checking words for improper capitalization
            else:
                separatorPosInNumber = numLength #Separator position if no delimiter following starting number 

        #Remove extension form filename
        if len(extension) > 0:
            nameWithoutExtension = newFilename[:-len(extension)]
        else:
            nameWithoutExtension = newFilename

        #Split into individual words
        words = nameWithoutExtension.split(args.filenameDelimiter)

        #Check for separator between number and name that should be skipped over
        separatorPosInString = wordPosition
        if separatorPosInString < len(words): #Avoid index out of bounds
            wordPosition += 1 #Assume there is a separator
            for x in words[separatorPosInString][separatorPosInNumber:]: #Skip starting number if separator is part of number
                if x.isalnum():
                    wordPosition -= 1 #Not a separator if it contains an alphanumerical character
                    break

        #----------------------------------------#
        # Change the Case of Words to Title Case #
        #----------------------------------------#
        if args.shouldChangeToTitleCase and not nameWithoutExtension.isupper(): #Skips filenames that are intentionally all capitals

            #Change first word in title to uppercase
            if wordPosition < len(words): #Avoid index out of bounds
                if wordPosition == 0:
                    start = numLength #Skip number if it exists in first word
                else:
                    start = 0
                success, words[wordPosition] = capitalizeFirstAlphanumeric(words[wordPosition], start)
                if success:
                    caseChanged = True
                wordPosition += 1
            
            #Check for inner words that should be lowercase or uppercase
            for pos in range(wordPosition, len(words) - 1): #Skip number (if it exists) and first and last words
                wordMatch = regex.wordPattern.match(words[pos])
                if wordMatch:
                    if words[pos-1][-1].isalnum(): #Only change to lowercase if word doesn't follow punctuation
                        words[pos] = words[pos].lower()
                        caseChanged = True
                    if words[pos] == "as":
                        filenameContainsTheWordAs = True
                else:
                    success, words[pos] = capitalizeFirstAlphanumeric(words[pos])
                    if success:
                        caseChanged = True

            #Change last word in title to uppercase
            success, words[-1] = capitalizeFirstAlphanumeric(words[-1])
            if success:
                caseChanged = True

        #-----------------------------------------------------------------#
        # Rebuild filename With Case-Changed Words and Replace Delimiters #
        #-----------------------------------------------------------------#        
        if caseChanged or args.shouldReplaceFilenameDelimiters:
            if args.shouldReplaceFilenameDelimiters:
                delimiter = args.newFilenameDelimiter
            else:
                delimiter = args.filenameDelimiter
            nameWithoutExtension = words[0]
            for word in words[1:]:
                nameWithoutExtension += delimiter + word
            fileRenamed = True

        #--------------------------------------------------------------#
        # Insert Leading Zero and Remove/Change Separator After Number #
        #--------------------------------------------------------------#
        if numLength > 0:
            #Insert leading zero if starting number is a single digit
            if args.shouldInsertLeadingZero and len(num) == 1:
                nameWithoutExtension = "0" + nameWithoutExtension
                num = "0" + num
                numLength += 1
                fileRenamed = True

            if len(args.newSeparator) > 0:
                if args.removeCount > 0:
                    offset = numLength + args.removeCount
                else:
                    offset = numLength
                    while offset < len(nameWithoutExtension) and not nameWithoutExtension[offset].isalnum():
                        offset += 1
                if offset <= len(nameWithoutExtension):
                    title = nameWithoutExtension[offset:]
                    nameWithoutExtension = num + args.newSeparator + title
                    fileRenamed = True


        #Add extension back to filename
        newFilename = nameWithoutExtension + extension

        #-------------------------------------------------#
        # Remove Spaces and Periods from End of Filenames #
        #-------------------------------------------------#
        while newFilename[-1] == ' ' or newFilename[-1] == '.':
            newFilename = newFilename[:-1]
            fileRenamed = True

        #--------------------------------------#
        # Display Each Filename Change to User #
        #--------------------------------------#
        if fileRenamed and newFilename != filename:
            if not changesPending:
                print("\n--The following changes will be made--\n")
                changesPending = True
            print("Old Name: " + filename)
            print("New Name: " + newFilename)
            oldFilenames.append(os.path.join(os.getcwd(), filename))
            newFilenames.append(os.path.join(os.getcwd(), newFilename))
            if filenameContainsTheWordAs:
                print("  --ATTENTION: The word \"as\" should be capitalized if followed by a verb. Please capitalize manually if needed--")
        elif filenameContainsTheWordAs: #Or warn user if filename contains the word "as"
            if not changesPending:
                print("\n--The following changes will be made--\n")
                changesPending = True
            print("Old Name: " + filename)
            print("  --ATTENTION: The word \"as\" should be capitalized if followed by a verb. Please capitalize manually if needed--")

    #---------------------------------------------#
    # Prompt User to Perform Changes to Filenames #
    #---------------------------------------------#
    if changesPending and len(newFilenames) > 0:
        performChanges(oldFilenames, newFilenames)
    else:
        print("\n--No filenames needing automatic changes were found--\n")

def performChanges(oldFilenames, newFilenames):
    """Prompt the user and rename the filenames if the user confirms they want to proceed"""
    proceed = input("\nType \"yes\" to proceed with the above changes: ")
    if proceed.lower() == 'yes':
        if(len(oldFilenames) != len(newFilenames)):
            print("ERROR: The list of original filenames is not the same length as the list of new filenames")
            exit()      
        for old, new in zip(oldFilenames, newFilenames):
            #Perform fix for case-insensitive filesystems that won't rename if only the case was changed
            #For example: If renaming "One For All" to "One for All", the OS will never rename it and always stay at "One For All"
            if platform.system() != 'Windows' and len(old) == len(new):
                os.rename(old, new + '-')
                os.rename(new + '-', new)
            else:
                os.rename(old, new)   
        print("\n--The above changes were successfully made--\n")
    else:
        print("\n--The above changes were not performed--\n")

def capitalizeFirstAlphanumeric(word, start = 0):
    """Capitalize first alphanuneric character in a word starting at the specified start position"""
    for i in range(start, len(word)):
        if word[i].isalnum(): #Get first alphanumeric character in word
            if word[i].islower(): #Change to uppercase if lowercase alphabet
                word = word[:i] + word[i].upper() + word[i+1:]
                return True, word
            break
    return False, word

def getCommandLineArguments():
    """Process the command-line arguments and return an Argument object containing the specified settings to be used"""
    global regex
    args = Arguments() #New argument object to be returned
    argvLength = len(sys.argv)
    if argvLength > 1:
        for i in range(argvLength):
            arg = sys.argv[i]
            if arg == "-f": #Only target files with the user-specified extension
                if argvLength > i + 1 and sys.argv[i + 1][0] != '-':
                    argFileType = sys.argv[i + 1]
                    if argFileType[0] == '.':
                        args.targetFileType = argFileType
                    else:
                        args.targetFileType = '.' + argFileType
                else:
                    print("ERROR: Filetype not specified")
                    print("To use the -f command, specify the filetype to target after the command. For example: -f .mp3")
                    exit()
            elif arg == "-s": #Remove characters after the starting number and replace with specified separator
                if argvLength > i + 1 and (sys.argv[i + 1][0] != '-' or len(sys.argv[i + 1]) == 1):
                    args.newSeparator = sys.argv[i + 1]
                    if regex.invalidPattern.search(args.newSeparator):
                        print("ERROR: Separator can't contain any of the following characters: " + regex.invalidCharacters + "\n")
                        exit()
                    elif regex.alnumPattern.search(args.newSeparator):
                        print("ERROR: Separator can't contain alphanumeric characters\n")
                        exit()
                    if argvLength > i + 2 and sys.argv[i + 2][0] != '-':
                        if not sys.argv[i + 2].isnumeric():
                            print("ERROR: Number was not specified")
                            exit()
                        args.removeCount = int(sys.argv[i + 2])
                        if args.removeCount < 0:
                            print("ERROR: Negative number was specified")
                            exit()
                else:
                    print("ERROR: Replacement separator not specified")
                    print("To use the -s command, specify the replacement separator you would like to use. For example: -s \". \"")
                    print("If original separator is not automatically removed, enter the number of characters to remove after the starting number. For example: -s \". \" 2")
                    exit()
            elif arg == "-d": #Use the user-specified delimiter to seperate words in the filename
                if argvLength > i + 1 and (sys.argv[i + 1][0] != '-' or len(sys.argv[i + 1]) == 1):
                    args.filenameDelimiter = sys.argv[i + 1]
                    if argvLength > i + 2 and (sys.argv[i + 2][0] != '-' or len(sys.argv[i + 2]) == 1):
                        args.shouldReplaceFilenameDelimiters = True
                        args.newFilenameDelimiter = sys.argv[i + 2]
                    if regex.invalidPattern.search(args.filenameDelimiter) or regex.invalidPattern.search(args.newFilenameDelimiter):
                        print("ERROR: Delimiter can't contain any of the following characters: " + regex.invalidCharacters + "\n")
                        exit()
                    elif regex.alnumPattern.search(args.filenameDelimiter) or regex.alnumPattern.search(args.newFilenameDelimiter):
                        print("ERROR: Delimiter can't contain alphanumeric characters\n")
                        exit()
                else:
                    print("ERROR: Delimiter not specified")
                    print("To use the -d command, specify the delimiter used to seperate words in the original filename. For example: -d _")
                    print("Optionally, a second delimiter can be specified to be used as a replacement. For example: -d _ .")
                    exit()
            elif arg == "-i": #Do not alter the filename's capitalization
                args.shouldChangeToTitleCase = False
            elif arg == "-z": #Insert leading zeros for single digit numbers
                args.shouldInsertLeadingZero = True
    return args

class Regex:
    """Regular expressions used to rename the filename and detect the proper format of user-entered variables"""
    numPattern = re.compile('[0-9]+')
    alnumPattern = re.compile('[0-9A-Za-z]')
    invalidPattern = re.compile(r'[\\/:*?"<>|]')
    invalidCharacters = r'\/:*?"<>|'

    def __init__(self):
        #Build regex string from the list of words       
        wordsRegex = ""
        if wordsToLower:
            wordsRegex += r'\b' + wordsToLower[0] + r'\b'
            for word in wordsToLower[1:]:
                wordsRegex += r'|\b' + word + r'\b'

        #Compile regular expressions
        self.wordPattern = re.compile(wordsRegex, re.IGNORECASE)

class Arguments:
    """Settings to be used based on the user-specified, command-line arguments"""
    removeCount = 0
    newSeparator = ""
    targetFileType = ""
    filenameDelimiter = " "
    newFilenameDelimiter = " "
    shouldReplaceFilenameDelimiters = False
    shouldChangeToTitleCase = True #This was always the original purpose of this script so I have left it enabled by default
    shouldInsertLeadingZero = False

if __name__ == '__main__':
     main()
