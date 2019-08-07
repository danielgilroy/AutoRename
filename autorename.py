#!/usr/bin/env python3

import os
import platform
import sys
import re
import glob

#List of words to be changed to lowercase
wordsToLower = ["The", "A", "An", "And", "But", "Or", "Nor", "At", "By", "For", "From", "In", "Into", 
                "Of", "Ov", "Off", "On", "Onto", "Out", "Over", "To", "Up", "With", "As"]
                #NOTE: The word "as" should be capitalized if it's followed by a verb 

def main():

    changesPending = False
    oldFilenames = []
    newFilenames = []

    #Build regex string from list of words           
    wordsRegex = ""
    if wordsToLower:
        wordsRegex += r'\b' + wordsToLower[0] + r'\b'
        for word in wordsToLower[1:]:
            wordsRegex += r'|\b' + word + r'\b'

    #Compile regular expressions
    caseSensitivePattern = re.compile(wordsRegex)
    caseInsensitivePattern = re.compile(wordsRegex, re.IGNORECASE)
    numPattern = re.compile('[0-9]+')
    alnumPattern = re.compile('[0-9A-Za-z]')
    invalidPattern = re.compile(r'[\\/:*?"<>|]')
    invalidCharacters = r'\/:*?"<>|'

    #Get user-specified filetype from argument or set to default filetype
    if len(sys.argv) > 1:
        if sys.argv[1][0] == '.':
            targetFileType = str(sys.argv[1])
        else:
            targetFileType = '.' + str(sys.argv[1])
    else:
        print("Every filetype is targeted by default: Use an argument to target a specific filetype")
        targetFileType = ""

    #Get the number of characters to be removed after the filename number
    removeCount = input("Enter the number of characters to remove after the filename number: ")
    if removeCount.isnumeric() and int(removeCount) > 0:    
        removeCount = int(removeCount)
    else:
        removeCount = 0

    #Get delimiter string to insert after the filename number
    while True:
        replaceWith = input("Enter a delimiter string to insert after the filename number: ")
        if invalidPattern.search(replaceWith):
            print("Delimiter can't contain any of the following characters: " + invalidCharacters + "\n")
        elif alnumPattern.search(replaceWith):
            print("Delimiter can't contain alphanumeric characters\n")
        else:
            break

    #Process every filename and create new filename string
    for filename in glob.glob('*' + targetFileType):

        fileRenamed = False
        caseChange = False
        newFilename = filename
        wordSkip = 0
        delimiterPosInNumber = 0 #Position of delimiter if part of the starting number: Assume it's not
        extension = os.path.splitext(filename)[1]
        numLength = 0

        #--------------------------------------#
        # Remove/Change Delimiter After Number #
        #--------------------------------------#
        numMatch = numPattern.match(filename)
        if numMatch: #Check for starting number in filename
            num = numMatch.group()
            numLength = numMatch.end()
            #Remove characters after filename number and replace with user-specified string 
            if removeCount > 0 or len(replaceWith) > 0:
                offset = numLength + removeCount
                if offset <= len(filename) - len(extension):
                    nameWithoutNum = filename[offset:]
                    newFilename = num + replaceWith + nameWithoutNum
                    fileRenamed = True
            #Check if number is seperated by a space
            if len(newFilename) > numLength and newFilename[numLength] == ' ': 
                wordSkip += 1 #Add one to skip starting number when checking words for improper capitalization
            else:
                delimiterPosInNumber = numLength #Delimiter position if no space following starting number 

        #--------------------------#
        # Change the case of words #
        #--------------------------#

        #Get filename without extension
        if len(extension) > 0:
            nameWithoutExtension = newFilename[:-len(extension)]
        else:
            nameWithoutExtension = newFilename

        words = nameWithoutExtension.split()

        #Check for delimiter between number and name that should be skipped over
        delimiterPosInString = wordSkip
        if delimiterPosInString < len(words): #Avoid index out of bounds
            wordSkip += 1 #Assume there is a delimiter
            for x in words[delimiterPosInString][delimiterPosInNumber:]: #Skip starting number if delimiter is part of number
                if x.isalnum():
                    wordSkip -= 1 #Not a delimiter if it contains an alphanumerical character
                    break

        #Change first word in title to uppercase
        if wordSkip < len(words): #Avoid index out of bounds
            if wordSkip == 0:
                start = numLength #Skip number if it exists in first word
            else:
                start = 0
            if capitalizeFirstAlphanumeric(words, wordSkip, start):
                caseChange = True
            wordSkip += 1
        
        #Check for inner words that should be lowercase or uppercase
        for pos in range(wordSkip, len(words) - 1): #Skip number (if exists) and first and last words
            wordMatch = caseSensitivePattern.match(words[pos])
            if wordMatch and words[pos-1][-1].isalnum():
                words[pos] = words[pos].lower() #Change word to lowercase
                caseChange = True
            else:
                wordMatch = caseInsensitivePattern.match(words[pos])
                if wordMatch and words[pos-1][-1].isalnum(): 
                    continue #Skip words that should be lowercase
                if capitalizeFirstAlphanumeric(words, pos): #Capitalize the first alphanumeric character if it's an alphabet
                    caseChange = True

        #Change last word in title to uppercase
        if wordSkip <= len(words) - 1: #Avoid index out of bounds
            if capitalizeFirstAlphanumeric(words, -1):
                caseChange = True

        #Rebuild filename if any words were changed to lowercase
        if caseChange:
            newFilename = ""
            newFilename += words[0]
            for word in words[1:]:
                newFilename += ' ' + word
            newFilename += extension
            fileRenamed = True

        #--------------------------#
        # Setup Changes To Be Made #
        #--------------------------#
        if fileRenamed:
            if filename == newFilename:
                continue #No need to rename if filenames are the same
            if not changesPending:
                print("\n--The following changes will be made--\n")
                changesPending = True
            oldFilenames.append(os.path.join(os.getcwd(), filename))
            newFilenames.append(os.path.join(os.getcwd(), newFilename))
            print("Old Name: " + filename)
            print("New Name: " + newFilename)
            if ' as ' in newFilename:
                print("    --ATTENTION: The word \"as\" should be capitalized if it\'s followed by a verb--")
            
    #------------------------------#
    # Perform changes to filenames #
    #------------------------------#      
    if changesPending:     
        performChanges(oldFilenames, newFilenames)
    else:
        print("\n--No filenames need changing--\n")
            

def performChanges(oldFilenames, newFilenames):
    #Rename the filenames if the user confirms they want to proceed     
    proceed = input("\nType \"yes\" to proceed with the above changes: ")
    if proceed.lower() == 'yes':
        if(len(oldFilenames) != len(newFilenames)):
            print("ERROR: The list of original filenames is not the same length as the list of new filenames")
            sys.exit()      
        for old, new in zip(oldFilenames, newFilenames):     
            if platform.system() != 'Windows' and len(old) == len(new):
                os.rename(old, new + '-') #Fix for case-insensitive filesystems
                os.rename(new + '-', new)
            else:
                os.rename(old, new)   
        print("\n--The above changes were successfully made--\n")
    else:
        print("\n--The above changes were not performed--\n")


def capitalizeFirstAlphanumeric(words, pos, start = 0):
    for i in range(start, len(words[pos])): 
        if words[pos][i].isalnum(): #Get first alphanumeric character in word
            if words[pos][i].islower(): #Change to uppercase if lowercase alphabet
                words[pos] = words[pos][:i] + words[pos][i].upper() + words[pos][i+1:]
                return True
            break
    return False


if __name__ == '__main__':
     main()
