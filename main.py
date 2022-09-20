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


r = sr.Recognizer()
mic = sr.Microphone()

play_file('assets/termination beep.mp3')
i = 0
while i < len(sequence):
    play_phrase(sequence[i])
    with mic as source:
        play_file('assets/end sentence beep.mp3')
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(text)
            if text == "abort":
                play_file('assets/processed/phrases/takeoff aborted.mp3')
                break
            if text in sequence[i]["responses"]:
                i += 1
        except Exception as e:
            print(e)
play_file('assets/termination beep.mp3')
