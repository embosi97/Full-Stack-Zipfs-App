from django.shortcuts import render, redirect
from .models import ZInfo
from django.utils.datastructures import MultiValueDictKeyError
#Necessary imports
import requests
import re
import platform
import sys
import codecs
import pytesseract
from bs4 import BeautifulSoup
from collections import Counter
from langdetect import detect
from datetime import date
from PIL import Image
from bokeh.plotting import figure, show
from bokeh.models import PolyAnnotation
from bokeh.core.enums import MarkerType
from bokeh.models import BoxAnnotation, Range1d
from bokeh.io import curdoc
from bokeh.models.tools import BoxZoomTool, PanTool, ResetTool, HoverTool
from bokeh.embed import components
import random
import os
import time, stat
import PyPDF2
from requests.exceptions import MissingSchema, InvalidURL

global alphanumeric
alphanumeric = "[^\w0-9 ]"

#Getting the operating system
def OS():
    oSystem = platform.system()  #Darwin, Linux, Java, and Windows
    return ('MacOS' if oSystem == 'Darwin' else oSystem)

#ZipfsSite object that stores the url, hash, the last modified date of the site or file (if it exists), and the final percent
class ZipfSite:
    def __init__(self, url, hash, last_modified, percentage, language):

        self.url = url
        self.hash = hash
        self.last_modified = last_modified
        self.percentage = percentage
        self.language = language

    def __str__(self):
        return self.url

#Directs to the home page
def HomePage(request):
    return render(request, 'build/homepage.html')

#This is where the selection between sites and files will be
def HubPage(request):
    return render(request, 'build/zhub.html')

#Returns a shortened URL
def truncateURL(url):
    #If the url string has a normal schema, make url into a substring of itself
    if '//' in url:
        url = url[url.rindex('//') + 2:len(url)]

        if url[len(url) - 1] == '/':
            url = url[:-1]

    return url

#Creating a bokeh plot that'll be displayed on the generated Zipf's app
def createBokehPlot(url, hash, zvalues):

    todayDate = date.today()

    hashLength = len(zvalues)

    wordList = list(hash.keys())

    #Generate list of rgb hex colors in relation to Y-axis
    colors = ["#%02x%02x%02x" % (255, int(round(value * 255 / 100)), 255) for value in zvalues]

    # create a new plot with a title and axis labels
    p = figure(
        x_range= wordList,
        title= f'Results for \'{url}\' \n {todayDate} \n {OS()}',
        x_axis_label = "Word Rank",
        y_axis_label= "Word Frequency",
        sizing_mode="stretch_width",
        toolbar_location="below",
        tools=[BoxZoomTool(), ResetTool(), HoverTool()],
        tooltips=f'Word \'@x\' has @y occurrances',
        )
    curdocColor = random.choice(["dark_minimal", "light_minimal"])
    curdoc().theme = curdocColor

    p.title.align = 'center'
    p.title.text_color = "gray" if curdocColor == 'light_minimal' else '#5cb85c'
    p.title.text_font_size = "18px"
    p.xaxis.major_label_orientation = "vertical"

    low_box = BoxAnnotation(top=zvalues[0]*.33, fill_alpha=0.3, fill_color='#d9534f')
    mid_box = BoxAnnotation(bottom=zvalues[0]*.33, top=zvalues[0]-(zvalues[0]*.33), fill_alpha=0.3, fill_color='#f0ad4e')
    high_box = BoxAnnotation(bottom=zvalues[0]-(zvalues[0]*.33), fill_alpha=0.3, fill_color='#5cb85c')

    p.add_layout(low_box)
    p.add_layout(mid_box)
    p.add_layout(high_box)

    # add a line renderer with legend and line thickness
    p.line(
        wordList,
        zvalues,
        line_color= "gray" if curdocColor == 'light_minimal' else '#5cb85c',
        line_width=2,
        )

    p.circle(
        wordList,
        zvalues,
        legend_label="Words",
        fill_color= colors,
        fill_alpha=.7,
        line_color= "black" if curdocColor == 'light_minimal' else '#5cb85c',
        size=9,
    )
    p.add_tools(PanTool(dimensions="width"))

    script, div = components(p)
    # show the results
    #show(p)
    return script, div

#Parsing function where a URL is passed as a parameter
#Supported languages are English, Spanish, German, and Italian
def parseSite(lang, url):
    #Requests the raw HTML text and assigns it to 'html'
    html = requests.get(url)

    global modified
    #Using BeutifulSoul's HTML parser to parse/sieve through the raw HTML text
    if 'Last-Modified' in html.headers:
        #Making modified a global variable so generateChart can access it without doing a requests call again
        modified = html.headers['Last-Modified']
    else:
        modified = 'N/A'

    soup = BeautifulSoup(html.text, "html.parser")

    #Initialize a Counter object (a subclass of dict that provides the frequencies for each word)
    count = Counter()

    #Going through the soup 'html'
    for word in soup.findAll('html'):
        #Utilizes the re module's sub methods to clean up the words (made lowercase) by replacing the regex pattern with ""
        text = re.sub(alphanumeric, "", word.get_text().lower())

        #Checks to see if the word is in a particular language
        if (detect(text) == lang):
            #Inserts the word into count (Counter object)
            count.update(text.split(" "))

    #Removing the key that is just a blank space
    del count['']
    #Returns the Counter object
    return count if len(count) > 10 else 0

#This function parses files instead of URL
#Supported files include '.txt', '.html', '.png', '.jpeg', '.jpg', '.doc', '.docx', and '.pdf'
def parseFile(file):

    #Getting the filename and extension by splitting text
    fileName, extension = file.name, file.name.split('.')[1]

    extension = f'.{extension}'

    hasDigits = re.compile('\d')

    count = Counter()

    #If the extension is a .txt, .doc, or docx file, proceed with parsing in this manner
    if extension == '.txt' or extension == '.docx' or extension == '.doc':

        with file as f:
            #Using a list comprehension to get the individual words, instead of lines of words
            word_list = [word.decode("utf-8") for line in f for word in line.split()]

            for line in word_list:
                #Using regex to remove non-alphabet letters
                text = re.sub(alphanumeric, "", line.lower())

                if (bool(hasDigits.search(text)) == False and len(text) > 0):
                    #Inserts the word into count (Counter object)
                    count.update(text.split())

    elif extension == '.html':

        #Similar steps to ParseSite's method of parsing words
        soup = BeautifulSoup(file, "html.parser")

        parsedHTML = soup.find('html')

        noTag = re.sub(alphanumeric, "", parsedHTML.get_text().lower())

        temp = []
        #extend the newly created list to the empty list
        temp.extend(noTag.split())

        for text in temp:

            if (bool(hasDigits.search(text)) == False and len(text) > 0):
                count.update(text.split(" "))

    #In the case the file is a pdf file
    elif extension == '.pdf':

        #This string will be used to store the extracted text from each page of the PDF
        stringBuilder = ''

        #Creating a PDF reader object
        pdfReader = PyPDF2.PdfFileReader(file, 'rb')

        #For-Loop that'll go through all the pages of the PDF
        #so all words can be put into the Counter object
        for i in range(0, pdfReader.numPages):

            #Each individual page of the PDF
            pageObject = pdfReader.getPage(i)

            #The extracted text is put into the string variable created above
            stringBuilder += ''.join(pageObject.extractText())

        #For-Loop to get all the individual words of the PDF
        for line in stringBuilder.split():

            text = re.sub(alphanumeric, "", line.lower())

            if (bool(hasDigits.search(text)) == False and len(text) > 0):
                count.update(text.split(" "))

    #In the case an image containing text is passed through
    elif extension == '.png' or extension == '.jpeg' or extension == '.jpg':
        #Python-tesseract is an optical character recognition (OCR) tool for python.
        #It will recognize and “read” the text embedded in images.
        stringBuilder = pytesseract.image_to_string(Image.open(file))

        for line in stringBuilder.split():

            text = re.sub(alphanumeric, "", line.lower())

            if (bool(hasDigits.search(text)) == False and len(text) > 0):
                count.update(text.split(" "))

    #If count is empty (when Django phase begins) or the extension is not supported
    elif extension not in ['.txt', '.html', '.png', '.jpeg', '.jpg', '.doc', '.docx', '.pdf']:
        return 0

    return count if len(count) > 10 else 0

#Function that'll calculate a percentage on the similarity to a pure zipf's chart
def percentageCount(hash):
    #Setting zvalues to the hash values converted to a list
    zvalues = list(hash.values())
    #Getting the most frequent word
    mostFreqWord = zvalues[0]
    #These will be used when returning the finals percentage
    percentSum = 0

    zipfPerfectPercent = 0
    #Iterating through the sorted top 100 words from the site
    #0(N) time algorithm that'll return the similarity percentage of the frequecies
    for i in range(0, len(zvalues) - 1):

        zdifference = (mostFreqWord / (2 + i))

        current = zvalues[1 + i]
        #This increments by 100 each time so we can compare how similar a perfect zipf's chart would be to the actual zipf's chart
        zipfPerfectPercent += 100

        #Calculates the percent difference between the ideal zipf's division (zdifference) and the division between the most frequent word/(2+i) and the current word (current)
        theDiff = ((zdifference / current) * 100)

        percentSum += theDiff

    #Rounding the final percent to 2 decimal points
    return round((percentSum / zipfPerfectPercent) * 100, 2), zvalues

#Function that takes URL as an argument and generates a chart from the Counter object returned by parseSite
def generateChart(request):
    #For parsing sites, there are 3 possible scenarios:
    # 1) The object is in the DB but doesn't need to be updated since the last_modified is not different
    # 2) Exists in the DB but has a different modified time, therefore needs to be updated
    # 3) Doesn't exist in the DB and is therefore a new object that has to be added
    try:
        if request.GET.get('siteURL'):
            #Get inputted URL
            url = str(request.GET.get('siteURL'))
            #Fetches the selected language
            language = str(request.GET.get('lang'))

            try:
                shortenedURL = truncateURL(url)

                #IF the object already exists in the DB
                zObject = ZInfo.objects.get(url = shortenedURL)

                #Since in this case there would already be an object with this URL, no need for a redirect
                word_count = parseSite(language, url)

                #If modified isn't the same, then we assume that hash and the percentage aren't either
                if (zObject.date != str(modified)):
                    try:
                        if len(word_count) >= 101:
                            hash = dict(word_count.most_common(101))
                        else:
                            hash = dict(word_count.most_common(len(word_count)))
                    except (TypeError):
                        return redirect("zhub") #Not enough parsed words in the Count object

                    percent, zvalues = percentageCount(hash)
                    script, div = createBokehPlot(shortenedURL, hash, zvalues)
                    percent = f'{percent}%'

                    objecty = ZipfSite(url = shortenedURL, hash = hash, last_modified = str(modified), percentage = percent, language = language)

                    #Updating a ZInfo object from Models and saving it into the PGDB
                    zObject.url = objecty.url
                    zObject.hash = objecty.hash
                    zObject.date = objecty.last_modified
                    zObject.percent = objecty.percentage
                    zObject.language = objecty.language

                    zObject.save()

                    return render(request, 'build/generatedZipf.html', {'percent': percent, 'script': script, 'div': div})

                else:
                    #If there is no conflict with the modified dates, just pass the pulled object
                    url = zObject.url
                    #The method getHash() is from Models and simply sorts the ZInfo object's hash (dict containing the words and their occurances)
                    hash = zObject.getHash()
                    percent = zObject.percent
                    script, div = createBokehPlot(url, hash, list(hash.values()))

                    return render(request, 'build/generatedZipf.html', {'percent': percent, 'script': script, 'div': div})

            #In the case the object doesn't exist in the DB, simply make a new ZInfo object in the DB
            except ZInfo.DoesNotExist:

                #Try-Catch that'll redirect the user if the URL is invalid or missing a schema (i.e. https)
                try:
                    word_count = parseSite(language, url)

                except (InvalidURL, MissingSchema):
                    #In the case the URL is not valid
                    return redirect('zhub')

                #Converting the Counter object to a dictionary so that we can better use the keys and values
                #To make plot and scatter chart
                try:
                    if len(word_count) >= 101:
                        hash = dict(word_count.most_common(101))
                    else:
                        hash = dict(word_count.most_common(len(word_count)))
                except (TypeError):
                    return redirect('zhub')

                #Calls this function to return the similarity percentage of the hash data
                percent, zvalues = percentageCount(hash)

                url = truncateURL(url)

                #Creating a bokeh chart that'll show the Zipf's pattern
                script, div = createBokehPlot(url, hash, zvalues)

                #Formatting the percent properly with the '%' sign
                percent = f'{percent}%'

                #Checks if the modified variable actually exists
                if 'modified' in globals():
                    objecty = ZipfSite(url = url, hash = hash, last_modified = str(modified), percentage = percent, language = language)
                else:
                    objecty = ZipfSite(url = url, hash = hash, last_modified = 'N/A', percentage = percent, language = language)

                #Creating a new ZInfo object from Models
                zObject = ZInfo(
                     url = objecty.url,
                     hash = objecty.hash,
                     date = objecty.last_modified,
                     percent = objecty.percentage,
                     language = objecty.language
                     )
                #Saving the newly created ZInfo object to the DB
                zObject.save()

                return render(request, 'build/generatedZipf.html', {'percent': percent, 'script': script, 'div': div})
        #In the case it's a File instead of a URL
        #File-based information will not be saved into the database
        else:
            #Requesting the file user inputted file
            uploadedFile = request.FILES['zFile']

            try:
                word_count = parseFile(uploadedFile)

            except (PyPDF2.utils.PdfReadError):
                #In case the PDF is corrupted
                return redirect("zhub") #Could not find xref table at specified location

            #Close the file since we already extracted the words
            uploadedFile.closed

            try:
                if len(word_count) >= 101:
                    hash = dict(word_count.most_common(101))
                else:
                    hash = dict(word_count.most_common(len(word_count)))
            except (TypeError):
                #If the file isn't supported or the Count object has less than 10 words
                return redirect("zhub")

            percent, zvalues = percentageCount(hash)

            script, div = createBokehPlot(uploadedFile, hash, zvalues)

            percent = f'{percent}%'

            return render(request, 'build/generatedZipf.html', {'percent': percent, 'script': script, 'div': div})
    #Checks for MultiValueDictKeyError which usually happens when no value is given for the URL
    except (MultiValueDictKeyError):

        return redirect('zhub')
