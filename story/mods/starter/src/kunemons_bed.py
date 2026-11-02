# Kunemon's Bed (screen 1): IceLeomon, on no other map of the island, has lost its medal. It asks, the tamer steps on the
# round stone (the trigger that maps/mayo02-stone.py adds), and it joins the city when it has its medal back. Its lines
# say "the white lion": the name the game shows is Panjyamon on the original disc and IceLeomon on Horizon.
#   README.md has the commands: the recipe runs first, because the trigger exists only in the recipe's map.
from dw import *

class LostMedal(Quest):
    NONE = auto()       # not asked yet (or you said no)
    ASKED = auto()      # you promised to look
    FOUND = auto()      # you stepped on the stone
    DONE = auto()       # it went to the city

bed = screen(Screen.kunemons_bed)

# A new NPC takes the screen's next free slot (`dws slots 1`). range=0 and still=True: it stands there and does not chase
# or patrol. It is there until it is recruited: `when=` is checked each time the screen loads.
iceleomon = bed.npc(Species.IceLeomon, at=(-750, -350), range=0, still=True, when=not recruited(Species.IceLeomon))

@iceleomon.on_talk(when=LostMedal.NONE)
def asks():
    say("I came down from the snow to rest in the warm grass, and now my medal is gone.",
        "It rolled west, towards the round stone. Would you look for it?")
    if ask(yes="I'll look", no="Not now"):
        say("Thank you. Step on the stone and you will see it.")
        advance(LostMedal.ASKED)
    else:
        say("Then I will wait here. It is warm, at least.")

@iceleomon.on_talk(when=LostMedal.ASKED)
def waits():
    say("The round stone, at the west end of this clearing. Please look there.")

@bed.on_step(1, when=LostMedal.ASKED)
def finds_the_medal():
    narrator.say("Something shines beside the round stone. It is the white lion's medal!")
    advance(LostMedal.FOUND)

@iceleomon.on_talk(when=LostMedal.FOUND)
def joins():
    say("My medal! You kept your word, Tamer.", "A city that has friends like you must be warm too. I will go and see it.")
    give(bits=500)
    narrator.say("Received 500 bits.")
    walk(-750, -50)
    advance(LostMedal.DONE)
    send_to_city(line="The white lion joined the city!", species=Species.IceLeomon)
