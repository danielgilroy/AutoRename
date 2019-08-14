
# Description

Auto Rename is a python application that automatically renames a group of filenames within a folder. It changes the first letter of every word to uppercase or lowercase according to the rules of capitalization for publications and works of art. It can also be used to remove or change the delimiter between the starting number and the title.

- Developed and tested on Windows and Linux using Python 3.6.8

## Example

The below filename will be changed as follows:

    01 This Is The Song Title Of A Song    =>    01 This Is the Song Title of a Song

Here are a few examples with delimiter changes:

    01 This Is The Song Title Of A Song    =>    01 - This Is the Song Title of a Song
    01 This Is The Song Title Of A Song    =>    01. This Is the Song Title of a Song

# Setup

Before using Auto Rename, it will be benefical to set it up so it can be ran from any directory. Otherwise a copy of Auto Rename will need to be in every directory that has files you want to rename. To set this up, you can either move Auto Rename to the proper system folder or you can modify the operating system's environment variables to include the folder where Auto Rename is located.

For Windows, move Auto Rename to the following folder:

    C:\Windows

For Linux, move Auto Rename to the following folder:

    /usr/local/bin

# Usage

To change the filename of every file in a folder, run the application without any arguments from a terminal window. The current working directory of the terminal will be the targeted directory for renaming files. 

    autorename.py

To only change the filename of specific filetypes, enter the filetype extension as an argument.

    autorename.py <file_extension>

To remove the delimiter between the starting number and the title, enter the number of characters to be removed. Note that the characters to be removed starts immediately after the starting number. So if "1" is entered for the number of characters to be removed, then the below filename will be changed as follows:

    Enter the number of characters to remove after the filename number: <1> 

    01 - This Is The Song Title Of A Song    =>    01- This Is the Song Title of a Song

Characters will only be removed from filenames that have a starting number since the intended use is to remove delimiters between the starting number and title. Be careful using this feature on multiple filenames containing dilimeters of different lengths as unintentional changes and even loss of filename data may occur. The following exaple demonstrates how filename data can be lost:

    Enter the number of characters to remove after the filename number: <2>

    01 - This Is The Song Title Of A Song    =>    01 This Is the Song Title of a Song
    02 This Is The Song Title Of A Song      =>    02His Is the Song Title of a Song

After entering the number of characters to be removed, a new delimiter string can be specified. A new delimiter will only be inserted if the filename has a starting number. If "3" is entered for the number of characters to remove and ". " for the delimiter, then the below title will be changed as follows:

    Enter the number of characters to remove after the filename number: <3>
    Enter a string to insert after the filename number: <. >

    01 - This Is The Song Title Of A Song    =>    01. This Is the Song Title of a Song

After entering the desired options, there will either be no filenames to change or a list of the old and new filenames displayed for review. Changes are not made until "yes" is entered as confirmation.

    --The following changes will be made--

    Old Name: 01 - This Is The Song Title Of A Song
    New Name: 01. This Is the Song Title of a Song

    Type "yes" to proceed with the above changes: <yes>

    --The above changes were successfully made--
