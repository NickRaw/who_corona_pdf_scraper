import PyPDF2
import PDFDownloader
from datetime import date, datetime, timedelta
import pycountry
import requests
from pathlib import Path
from io import BytesIO

link = 'https://www.who.int/docs/default-source/coronaviruse/situation-reports/{}-sitrep-{}-covid-19.pdf' # Link to the pdf

firstDate = datetime.strptime("21-1-2020", "%d-%m-%Y").date() # Date of first publication

countries=[f.name for f in pycountry.countries] # List of all countries in pycountry
# TODO: Figure out how to read every country. NLTK.Word_tokenizer?

def pdf_exists(link):
    response = requests.get(link, stream = True)
    if response.status_code == 404:
        return False
    else:
        return True

def get_pdf_stream(link):
    response = requests.get(link)
    pdf_file = BytesIO(response.content)
    return pdf_file

def prepare_WHO_grabberdata(date): # Takes a date and gives a formatted date en number back to use in the link
    issuenumber = (date-firstDate).days + 1
    if date.month < 10:
        str_month = "0"+str(date.month)
    else:
        str_month = str(date.month)
    strToday = str(date.year)+str_month+str(date.day)
    return strToday, issuenumber


def get_latest_WHO_Data():
    # Date and issue of today
    today = datetime.now().date()
    strToday, issuenumber_today = prepare_WHO_grabberdata(today)

    # Date and issue of yesterday
    yesterday = today - timedelta(1)
    strYesterday, issuenumber_yesterday = prepare_WHO_grabberdata(yesterday)

    data = [] # Empty list of data
    headers = ['country','total confirmed cases','total deaths','total new deaths'] # List of headers

    searchlink = link.format(strToday, str(issuenumber_today)) # Creating the link and checking if issue of today exists
    if pdf_exists(searchlink):
        # get filestream
        pdfFileObj = get_pdf_stream(searchlink)
    else:
        searchlink = link.format(strYesterday, str(issuenumber_yesterday))
        # get filestream
        pdfFileObj = get_pdf_stream(searchlink)

    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    #### Convert data from pdf into list of dictionaries ####
    for pageNum in range(0,pdfReader.getNumPages()):
        page = pdfReader.getPage(pageNum)
        splitpage = page.extractText().split("\n")

        header_place = 0
        datarow = {}
        for x in range(0, len(splitpage)):
            if splitpage[x] in countries:
                datarow[headers[header_place]] = splitpage[x]
                header_place += 1
            try:
                if header_place > 0:
                    number = int(splitpage[x])
                    datarow[headers[header_place]] = number
                    if header_place == len(headers)-1:
                        data.append(datarow)
                        header_place = 0
                        datarow = {}
                    else:
                        header_place += 1
            except ValueError as e:
                e = e

    pdfFileObj.close()
    print('Done')
    return data, headers

def sort_WHO_data_high_to_low(data):
    sorted_data = sorted(data, key=lambda i:i['cases'], reverse=True)
    for x in range(1,len(sorted_data)+1):
        sorted_data[x-1]['index'] = x
    return sorted_data

def sort_WHO_data_low_to_high(data):
    sorted_data = sorted(data, key=lambda i:i['cases'])
    for x in range(1, len(sorted_data)+1):
        sorted_data[x]['index'] = x
    return sorted_data


data, headers = get_latest_WHO_Data()

for country in data:
    print(country)