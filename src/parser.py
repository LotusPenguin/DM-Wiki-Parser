import os
import shutil
import urllib.request
from datetime import datetime
from dependencies.realesrgan import inference_realesrgan

from config import *
from utils import *


def formatText(text, card_type):
    text = stringButBetter(text)
    text = applyInconsistencyFixes(text)
    text = applyTextFormattingFixes(text)
    text = applyShieldTriggerCardTypeFixes(card_type, text)
    text = f'<b>{text}</b>'
    return text


def tagSubstitution(text: str):
    text = text.replace('<', '')
    return text


def applyShieldTriggerCardTypeFixes(card_type, text):
    if 'Creature' in card_type:
        text = text.replace(
            "(When this Card Type is put into your hand from your shield zone, you may use it for no cost.)",
            "(When this creature is put into your hand from your shield zone, you may summon it for no cost.)"
        )
    elif card_type == 'Spell':
        text = text.replace(
            "(When this Card Type is put into your hand from your shield zone, you may use it for no cost.)",
            "(When this spell is put into your hand from your shield zone, you may cast it for no cost.)"
        )
    elif card_type == 'Tamaseed':
        text = text.replace(
            "(When this Card Type is put into your hand from your shield zone, you may use it for no cost.)",
            "(When this tamaseed is put into your hand from your shield zone, you may use it for no cost.)"
        )
    return text


def applyTextFormattingFixes(text):
    text = tagSubstitution(text)
    text = (text
            .strip('[]')
            .replace('​​', '\n')
            .replace('​', '\n')
            .strip('\n')
            .replace('\n\n', '\n')
            .replace('\n\n', '\n')
            .replace('\n\n', '\n')
            .replace('\n', '\n\t\t')
            .replace('(', '<i>(')
            .replace(')', ')</i>')
            .replace('▼', '<sym>t</sym>➤')
            .replace('►', '<sym>t</sym>➤')
            .replace('▶', '<sym>t</sym>➤')
            .replace('HASHsymHASH', '<sym>')
            .replace('HASH/symHASH', '</sym>')
            )
    return text


def applyInconsistencyFixes(text):
    # Guard Strike inconsistency fix
    text = text.replace(
        "(When you add this creature from your shield zone to your hand, you may reveal it to your opponent and choose one of your opponent's creatures. That creature can't attack this turn.\n",
        "(When you add this creature from your shield zone to your hand, you may reveal it to your opponent and choose one of your opponent's creatures. That creature can't attack this turn.)\n"
    )
    return text


def generateFileBeginning(file):
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


def generateCardEntry(file, setName, card, index, includeFlavorText, enableUpscaling):
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    card_name = tagSubstitution(card['Name'])

    try:
        cost_text = card['Mana Cost']
    except KeyError:
        cost_text = ""
        println(f"No cost found for {card_name}")

    card_type = card['Card Type'].strip()
    match card_type:
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
    power_number_value = power_number.replace("+", "").replace("-", "")

    if power_number_value == "":
        power_text = ""
    elif power_number_value == "∞":
        power_text_number = 1
    elif int(power_number_value) < 10000:
        power_text_number = 1
    else:
        power_text_number = 2

    if '+' in power_number or '-' in power_number:
        power_text_number += 1

    if power_text_number > 0:
        power_text = str(power_text_number)
    else:
        power_text = ""

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

    upscaled_image_directory = parser_directory + setName
    # ESGRAN integration
    if enableUpscaling:
        raw_image_path = raw_image_directory + setName + f'/image{index}.png'
        image = urllib.request.urlretrieve(card['Image Url'], raw_image_path)
        inference_realesrgan.upscale(setName, raw_image_path, upscaled_image_directory)
    else:
        image = urllib.request.urlretrieve(card['Image Url'], upscaled_image_directory)

    try:
        text_formatted = formatText(card['English Text + Symbols'], card_type)
    except KeyError:
        text_formatted = ""

    if includeFlavorText:
        try:
            flavor_text = card['Flavor Text']
        except KeyError:
            flavor_text = ""
    else:
        flavor_text = ""

    if card_subtype != "" and type_text == 's':
        civspell_text = '1'
    else:
        civspell_text = ''

    if card_subtype != "" and type_text == 's':
        type_color = '1'
    elif 'c' in symbol_text or 'j' in symbol_text:
        type_color = '1'
    else:
        type_color = ''

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
\t\t<font:ITC Officina Sans>{flavor_text}<size:40></size></font>
\teffect: 
\t\t{text_formatted}
\ttext: 
\t\t{text_formatted}<sep><line>
\t\t</line></sep><font:ITC Officina Sans><size:40>{flavor_text}</size></font>
\tname: {card_name}
\tsubtype: {card_subtype}
\tcivspell_text: {civspell_text}
\ttype_color: {type_color}
""")


def removeFileSuffixes(setName):
    for file in os.listdir(parser_directory + setName):
        os.rename(os.path.join(parser_directory, setName, file),
                  os.path.join(parser_directory, setName, file).removesuffix('.png'))


def makeSet(setName, cardDetailsList, includeFlavorText=False, enableUpscaling=True):
    os.makedirs(parser_directory + setName, exist_ok=True)
    os.makedirs(raw_image_directory + setName, exist_ok=True)
    with open(parser_directory + setName + '/set', 'w', encoding='UTF-8') as setFile:
        generateFileBeginning(setFile)
        i = 1
        for card in cardDetailsList:
            i += 1
            generateCardEntry(setFile, setName, card, i, includeFlavorText, enableUpscaling)
        generateFileEnd(setFile)

    removeFileSuffixes(setName)

    shutil.make_archive(parser_directory + setName + '.mse-set', 'zip', parser_directory + setName)

    if os.path.exists(parser_directory + setName + '.mse-set'):
        os.remove(parser_directory + setName + '.mse-set')
    os.rename(parser_directory + setName + '.mse-set.zip', parser_directory + setName + '.mse-set')
