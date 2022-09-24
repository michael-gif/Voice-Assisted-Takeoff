import pygame
import json

import speech_recognition as sr

pygame.mixer.init()

callsign = ""
runway = "fff"
with open('assets/structures.json') as f:
    structures = json.load(f)
sequence = [
    {
        "structure": ["[callsign]", "e", "[runway]"],
        "responses": ["affirmative"]
    },
    {
        "structure": ["[callsign]", "c", "[runway]"],
        "responses": ["affirmative"]
    },
    {
        "structure": ["[callsign]", "d", "[runway]"],
        "responses": ["confirm", "confirmed"]
    },
    {
        "structure": ["[callsign]", "b"],
        "responses": ["check complete", "check completed", "checklist complete", "checklist completed"]
    },
    {
        "structure": ["[callsign]", "a"],
        "responses": ["affirmative"]
    }
]

phrases = {
    "a": "assets/processed/phrases/clear for takeoff.mp3",
    "b": "assets/processed/phrases/complete pre-flight check.mp3",
    "c": "assets/processed/phrases/proceed to runway.mp3",
    "d": "assets/processed/phrases/confirm runway.mp3",
    "e": "assets/processed/phrases/authorised for takeoff.mp3"
}
nato_phonics = {
    "a": "alfa",
    "b": "bravo",
    "c": "charlie",
    "d": "delta",
    "e": "echo",
    "f": "foxtrot",
    "g": "golf",
    "h": "hotel",
    "i": "india",
    "j": "juliett",
    "k": "kilo",
    "l": "lima",
    "m": "mike",
    "n": "november",
    "o": "oscar",
    "p": "papa",
    "q": "quebec",
    "r": "romeo",
    "s": "sierra",
    "t": "tango",
    "u": "uniform",
    "v": "victor",
    "w": "whiskey",
    "x": "x-ray",
    "y": "yankee",
    "z": "zulu",
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
}


def play_callsign(callsign: str):
    for char in callsign.lower():
        play_file(f'assets/processed/{nato_phonics[char]}.mp3')


def play_runway(runway: str):
    for char in runway.lower():
        play_file(f'assets/processed/{char}.mp3')


def play_file(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass


def play_phrase(phrase):
    for chunk in phrase["structure"]:
        if chunk == "[callsign]":
            play_callsign(callsign)
        elif chunk == "[runway]":
            play_runway(runway)
        else:
            play_file(phrases[chunk])


def starts_with_phrase(string, phrase_list):
    for phrase in phrase_list:
        if string.startswith(phrase):
            return phrase
    return False


def contains_phrase(string, phrase_list):
    for phrase in phrase_list:
        if phrase in string:
            return phrase
    return False


def string_to_number(string):
    alphabetic_numbers = [
        ["zero"],
        ["one", "won"],
        ["two", "to", "too", "tew", "thuy", "tue", "tui"],
        ["three"],
        ["four", "faure", "fore"],
        ["five"],
        ["six"],
        ["seven"],
        ["eight", "ait", "ate", "aydt"],
        ["nine"],
    ]
    for i in range(10):
        if string in alphabetic_numbers[i]:
            return i
    return False


def convert_to_natophonetic(raw_callsign):
    output = []
    items = raw_callsign.split(" ")
    for item in items:
        if item.isdigit():
            output.append(item)
            continue
        result = string_to_number(item.lower())
        if result:
            output.append(str(result))
        else:
            output.append(item.lower()[0])
    return ''.join(output)


sentence_structure = {
    "tower": [
        "aicraft traffic control this is",
        "aircraft traffic controller this is",
        "air traffic control this is",
        "air traffic controller this is",
        "towah this is",
        "tower this is",
        "towel this is"
    ],
    "[callsign]": [
        "[callsign]"
    ],
    "permission": [
        "requesting permission",
        "request permission",
        "requested permission"
    ],
    "take off": [
        "to take of from",
        "to take of from",
        "to take off from",
        "to take off from",
        "too take of from",
        "too take of from",
        "too take off from",
        "too take off from",
        "to take over from",
        "too take over from",
        "to land on",
        "to land on",
        "too land on",
        "too land on"
    ],
    "runway": [
        "runway",
        "runaway",
        "run way",
        "one way",
        "one-way",
        "the runway",
        "the runaway",
        "the run way",
        "the one way",
        "the one-way"
    ],
    "[runway]": [
        "[runway]"
    ]
}


def tokenise_text(text):
    for struct in structures:
        tokens = {}
        tmp = text
        prev_keys = []
        current_node = [node for node in struct['nodes'] if node['id'] == 0][0]
        result = starts_with_phrase(text, current_node['possibilities'])
        if not result:
            continue
        for i in range(len(struct['nodes'])):
            current_node = [node for node in struct['nodes'] if node['id'] == i][0]
            #print("current node: " + str(current_node))
            result = contains_phrase(text, current_node['possibilities'])
            #print("Result: " + str(result))
            if result:
                tmp_2 = tmp.split(result)
                #print(tmp_2)
                if tmp_2[0] != '':
                    tokens[prev_keys[-1]] = tmp_2[0].strip()
                tokens[current_node['name']] = result
                #print("Tokens: " + str(tokens))
                tmp = tmp_2[1].strip()
                #print("tmp: " + tmp)
            prev_keys.append(current_node['name'])
        tokens[current_node['name']] = tmp.strip()
    #print("Tokens: " + str(tokens))
    for key in [node['name'] for node in struct['nodes']]:
        if key not in tokens.keys():
            return False
    return convert_to_natophonetic(tokens["[callsign]"]), convert_to_natophonetic(tokens["[runway]"])


r = sr.Recognizer()
mic = sr.Microphone()

can_continue = False
while not can_continue:
    with mic as source:
        play_file('assets/end sentence beep.mp3')
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(text)
            chunks = tokenise_text(text.strip())
            print(chunks)
            if chunks:
                can_continue = True
                callsign, runway = chunks
            else:
                play_file('assets/termination beep.mp3')
        except Exception as e:
            print(e)

play_file('assets/termination beep.mp3')
i = 0
while i < len(sequence):
    play_phrase(sequence[i])
    with mic as source:
        play_file('assets/end sentence beep.mp3')
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            if text == "abort":
                play_file('assets/processed/phrases/takeoff aborted.mp3')
                break
            if text in sequence[i]["responses"]:
                i += 1
        except Exception as e:
            print(e)
play_file('assets/termination beep.mp3')
