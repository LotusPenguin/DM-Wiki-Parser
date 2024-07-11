import json
import os
import time
import argparse

import requests
from bs4 import BeautifulSoup, Tag

from config import *
from parser import makeSet
from utils import *


def getPageResponse(URL):
    println(URL)
    while True:
        try:
            return requests.get(URL)
        except:
            time.sleep(5)


def find_previous_of_tag(tag, to_find):
    prev_tag = tag.previous_sibling
    try:
        while not isinstance(prev_tag, Tag) or to_find != prev_tag.name:
            prev_tag = prev_tag.previous_sibling
        return prev_tag
    except Exception:
        return None


def includeSymbols(text):
    text = text.replace('data-image-name="', 'data-image-name=>HASHsymHASH').replace('" data-relevant',
                                                                                     'HASH/symHASH<data-relevant')
    temp_soup = BeautifulSoup(text, 'html.parser')
    text = temp_soup.get_text()
    return text


def getCards(linkList):
    returnedList = []
    for cardLink in linkList:
        try:
            cardPage = requests.get(cardLink, timeout=60)
            cardPageParsed = BeautifulSoup(cardPage.content, "html.parser")
            cardPageContent = cardPageParsed.find('table', class_='wikitable').find('tbody')
            cardPageContentRows = cardPageContent.find_all('tr')

            cardDict = {}
            name = cardPageContentRows[0].find('th').find('div').find(string=True, recursive=False)
            cardPageContentRows.pop(0)
            cardDict['Name'] = name
            println(name)
            imageUrl = cardPageContentRows[0].find('a', class_='image')['href']
            cardDict['Image Url'] = imageUrl
            cardPageContentRows.pop(0)
            cardPageContentRows.pop(-1)
            cardPageContentRows.pop(-1)
            setsAndRarityRow = cardPageContentRows.pop(-1)
            setsAndRarityRowContent = setsAndRarityRow.find('div', class_='mw-collapsible mw-open')
            rarityTextRaw = setsAndRarityRowContent.find_all('b')  # For future use
            rarityText = setsAndRarityRowContent.get_text()
            cardPageContentRows.pop(-1)
            for element in cardPageContentRows:
                tempString = element.get_text()
                tempString = tempString.replace("\n", "")
                tempSplit = tempString.split(':', 1)
                cardDict[tempSplit[0]] = tempSplit[1]
                if 'English' in tempSplit[0]:
                    raw_text = includeSymbols(str(element.contents[3:]))
                    cardDict['English Text + Symbols'] = raw_text
            cardDict['Rarity Text'] = rarityText
            # cardDict['Rarity Text Raw'] = rarityTextRaw  # For future use
            returnedList.append(cardDict)
        except IndexError:
            println(IndexError)
    return returnedList


if __name__ == '__main__':
    os.makedirs(parser_directory, exist_ok=True)
    os.makedirs(scrapped_directory, exist_ok=True)
    os.makedirs(raw_image_directory, exist_ok=True)

    MODE = ""
    BASE_URL = "https://duelmasters.fandom.com"

    parser = argparse.ArgumentParser(description='CLI Interface for DM Wiki Parser')
    parser.add_argument('--source', type=str, required=True,
                        help='Dataset source directory.')
    parser.add_argument('--verbose', action='store_true',
                        help='Print debug info.')
    parser.add_argument('--name', type=str, required=False, default='',
                        help='Custom name for the set file.')
    parser.add_argument('--no_upscale', action='store_true',
                        help='Disable upscaling')
    parser.add_argument('--flavor_text', action='store_true',
                        help='Add flavor text')
    args = parser.parse_args()

    source = args.source
    verbose = args.verbose
    setName = args.name
    includeFlavorText = args.flavor_text
    enableUpscaling = not args.no_upscale

    cardLinksList = []

    start = time.time()

    if os.path.isfile(source):
        mode = 'link_list_in_file'
        with open(source) as f:
            cardLinksList = f.read().splitlines()
        if setName == '':
            setName = time.strftime('%Y-%m-%d %H-%M-%S')
    else:
        mode = 'set_url'
        SET_URL = source

        page = requests.get(SET_URL)
        soup = BeautifulSoup(page.content, "html.parser")

        mainPageContent = soup.find('div', class_='mw-parser-output')
        raritySectionListUnfiltered = mainPageContent.find_all('ul')
        raritySectionListFiltered = []
        for element in raritySectionListUnfiltered:
            sectionHeader = find_previous_of_tag(element, to_find='h2')
            if sectionHeader is not None:
                tempTag = sectionHeader.find('span')
                if tempTag is not None and tempTag.get_text() == 'Contents':
                    raritySectionListFiltered.append(element)

        for element in raritySectionListFiltered:
            tempList = element.find_all('a')
            for subElement in tempList:
                cardLinksList.append(BASE_URL + subElement['href'])
        if setName == '':
            setName = SET_URL.split('/')[-1].split('_')[0].strip()

    cardDetailsList = getCards(cardLinksList)

    ## Dump set details to file
    with open(scrapped_directory + setName + '.json', 'w', encoding='UTF-8') as f:
        for card in cardDetailsList:
            f.write(json.dumps(card) + '\n')

    makeSet(setName, cardDetailsList, includeFlavorText, enableUpscaling)

    end = time.time()
    println(f"Elapsed time: {end - start}")
