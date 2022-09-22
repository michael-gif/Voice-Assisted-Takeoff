import pygame
import speech_recognition as sr

pygame.mixer.init()

callsign = input("CALLSIGN: ")
runway = input("RUNWAY: ")
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
        "towel this is"],
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
        "too land on",
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
    tokens = {}
    tmp = text

    prev_keys = []
    for key, phrase_list in sentence_structure.items():
        phrase_list = sentence_structure[key]
        result = contains_phrase(text, phrase_list)
        #print("Result: " + str(result))
        if result:
            tmp_2 = tmp.split(result)
            #print(tmp_2)
            if tmp_2[0] != '':
                tokens[prev_keys[-1]] = tmp_2[0].strip()
            tokens[key] = result
            #print("Tokens: " + str(tokens))
            tmp = tmp_2[1].strip()
            #print("tmp: " + tmp)
        else:
            if len(prev_keys) == len(sentence_structure.keys()) - 1:
                tokens[key] = tmp.strip()
        prev_keys.append(key)
    #print("Tokens: " + str(tokens))
    for key in sentence_structure.keys():
        if key not in tokens.keys():
            return False
    return (convert_to_natophonetic(tokens["[callsign]"]), convert_to_natophonetic(tokens["[runway]"]))

    '''phrases = [
        "aicraft traffic control this is",
        "aircraft traffic controller this is",
        "air traffic control this is",
        "air traffic controller this is",
        "towah this is",
        "tower this is",
        "towel this is"]
    tower = starts_with_phrase(text, phrases)
    if tower:
        temp = [item.strip() for item in text.split(tower)]
        phrases = ["requesting permission",
                   "request permission",
                   "requested permission"]
        permission = contains_phrase(temp[1], phrases)
        if permission:
            temp_2 = temp[1].split(permission)
            raw_callsign = temp_2[0].strip()
            callsign = convert_to_natophonetic(raw_callsign)
            print("Extracted callsign: " + callsign)
            phrases = [
                "to take of from",
                "to take of from",
                "to take off from",
                "to take off from",
                "too take of from",
                "too take of from",
                "too take off from",
                "too take off from",
                "to land on",
                "to land on",
                "too land on",
                "too land on"
            ]
            temp_3 = starts_with_phrase(temp_2[1].strip(), phrases)
            if temp_3:
                temp_4 = temp_2[1].strip().split(temp_3)[1].strip()
                phrases = [
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
                ]
                temp_5 = starts_with_phrase(temp_4, phrases)
                if temp_5:
                    raw_runway = temp_4.split(temp_5)[1].strip()
                    print(raw_runway)
                    runway = convert_to_natophonetic(raw_runway)
                    print("Extracted runway: " + runway)
                    return (callsign, runway)
    else:
        return False'''


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
