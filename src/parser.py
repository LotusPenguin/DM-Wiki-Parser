import os
import shutil
import urllib.request
from datetime import datetime

from config import *
from utils import stringButBetter


# TODO: change text source to formatted raw to preserve symbol usage (eliminates issues with different wording etc.
def formatText(text):
    text = f'<b>{text}</b>'
    text = stringButBetter(text)
    text = (text
            .replace('​', '')
            .replace('■', '\n\t\t■')
            .replace('(', '<i>(')
            .replace(')', ')</i>')
            .replace('Blocker', '\n\t\t<sym>Blocker</sym> Blocker')
            .replace_nth('Shield Trigger Plus', '\n\t\t<sym>Shield Trigger Plus</sym>Shield Trigger Plus', 1)
            .replace('►', '\n\t\t➤')

            .replace_nth('\n', '', 1)
            )
    return text


def generateFileBeggining(file):
    file.write("""mse_version: 2.0.2
game: duel-masters
game_version: 0.0.0
stylesheet: style
stylesheet_version: 0.0.0
""")


def generateFileEnd(file):
    file.write("""version_control:
\ttype: none
apprentice_code:
""")


def generateCardEntry(file, setName, card, index):
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cost_text = card['Mana Cost']

    match card['Card Type']:
        case "Creature":
            type_text = 'c'
        case "Spell":
            type_text = 's'
        case "Tamaseed":
            type_text = 't'
        case "Cross Gear":
            type_text = 'cg'
        case "Evolution Creature":
            type_text = 'e'
        case "Neo Creature":
            type_text = 'n'
        case _:
            type_text = ''

    try:
        power_number = card['Power']
    except KeyError:
        power_number = ""

    power_text_number = 0
    if '+' in power_number:
        power_text_number += 1
        power_number = power_number.replace("+", "")

    if power_number == "":
        power_text = ""
    elif int(power_number) < 10000:
        power_text_number = 1
    else:
        power_text_number = 2

    if power_text_number > 0:
        power_text = str(power_text_number)

    try:
        card_civ = card['Civilization']
    except KeyError:
        card_civ = card['Civilizations']

    try:
        card_subtype = card['Race']
    except KeyError:
        try:
            card_subtype = card['Races']
        except KeyError:
            card_subtype = ""
    card_subtype = card_subtype.upper()

    symbol_text = ""

    if 'Light' in card_civ:
        symbol_text += 'l'
    if 'Water' in card_civ:
        symbol_text += 'w'
    if 'Darkness' in card_civ:
        symbol_text += 'd'
    if 'Fire' in card_civ:
        symbol_text += 'f'
    if 'Nature' in card_civ:
        symbol_text += 'n'
    if 'Colorless' in card_civ:
        symbol_text += 'c'
    if 'Jokers' in card_subtype:
        symbol_text += 'j'

    image = urllib.request.urlretrieve(card['Image Url'], parser_directory + setName + f'/image{index}')

    # TODO: Italics and symbol replacement
    text_formatted = formatText(card['English Text'])
    card_name = card['Name']

    file.write(f"""card:
\thas_styling: false
\tnotes:
\ttime_created: {time_now}
\ttime_modified: {time_now}
\tcost_text: {cost_text}
\ttype_text: {type_text}
\tpower_text: {power_text}
\tpower_number: {power_number}
\tsymbol_text: {symbol_text}
\timage: image{index}
\tflavor: 
\t\t<font:ITC Officina Sans><size:40></size></font>
\teffect: 
\t\t{text_formatted}
\ttext: 
\t\t{text_formatted}<sep><line>
\t\t</line></sep><font:ITC Officina Sans><size:40></size></font>
\tname: {card_name}
\tsubtype: {card_subtype}
""")


def makeSet(setName, cardDetailsList):
    os.makedirs(parser_directory + setName, exist_ok=True)
    with open(parser_directory + setName + '/set', 'w', encoding='UTF-8') as setFile:
        generateFileBeggining(setFile)
        i = 1
        for card in cardDetailsList:
            i += 1
            generateCardEntry(setFile, setName, card, i)
        generateFileEnd(setFile)

    shutil.make_archive(parser_directory + setName + '.mse-set', 'zip', parser_directory + setName)

    if os.path.exists(parser_directory + setName + '.mse-set'):
        os.remove(parser_directory + setName + '.mse-set')
    os.rename(parser_directory + setName + '.mse-set.zip', parser_directory + setName + '.mse-set')
