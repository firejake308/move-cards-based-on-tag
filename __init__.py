import re
from aqt.utils import showInfo, qconnect
from aqt.qt import QAction
from aqt import mw

def find_deck_startswith(start):
    decks = seq = mw.col.decks.all_names_and_ids()
    for deck in decks:
        if deck.name.startswith(start):
            return mw.col.decks.by_name(deck.name)
    return None

def move_to_anking():
    cards = mw.col.find_cards("deck:HassAnki tag:#AK_Original_Decks")
    for card_id in cards:
        card = mw.col.get_card(card_id)
        tag_name = None
        for tag in card.note().tags:
            if tag.startswith('#AK_Original_Decks'):
                tag_name = tag
                break
        if tag_name is None:
            showInfo('Impossible error')
            return
        # hard-coding to fix a typo
        if tag_name == "#AK_Original_Decks::Step_2::Cheesy_Dorian_(M3)7":
            tag_name = tag_name[:-1]
        deck_name = tag_name.replace('#AK_Original_Decks', 'AnKing').replace('_', ' ')
        deck_name = deck_name.replace("Shouldnt", "Shouldn't")
        deck = mw.col.decks.by_name(deck_name)
        if deck is None:
            showInfo(f"Could not find deck: {deck_name}")
        card.did = deck['id']
        card.flush()
    showInfo(f"Moved {len(cards)} cards to AnKing")

def move_to_hassanki():
    cards = mw.col.find_cards("deck:AnKing tag:#BCM")
    for card_id in cards:
        card = mw.col.get_card(card_id)
        tag_name = None
        # I'm hoping that reverse sort will prioritize later term tags over earlier terms
        # e.g. Term 5 > Term 4
        # and the filter is supposed to cut down the runtime by reducing sort time
        for tag in sorted(filter(lambda tag: tag.startswith('#BCM'), card.note().tags), reverse=True):
            if  re.match(r"#BCM::.+::\d\d", tag) is not None:
                tag_name = tag
                break
        if tag_name is None:
            # maybe it was like #BCM::Extra
            continue
        deck_name = tag_name.replace('#BCM', 'HassAnki').replace('_', ' ')
        # only match on the beginning until the lecture number
        deck_name = re.match(r".+::\d\d", deck_name)[0]
        deck = find_deck_startswith(deck_name)
        did = None
        if deck is None:
            did = mw.col.decks.id(tag_name.replace('#BCM', 'HassAnki').replace('_', ' '))
        else:
            did = deck['id']
        card.did = did
        card.flush()
    showInfo(f"Moved {len(cards)} cards to HassAnki")

def rename_tags():
    num_changed = 0
    num_changed += mw.col.tags.rename("#BCM::Pharmacology", "#BCM::Term_3::Pharmacology").count
    num_changed += mw.col.tags.rename("#BCM::IPBD", "#BCM::Term_3::IPBD").count
    num_changed += mw.col.tags.rename("#BCM::Anatomy", "#BCM::Term_3::Anatomy").count
    num_changed += mw.col.tags.rename("#BCM::Infectious_Disease", "#BCM::Term_4::Infectious_Disease").count
    num_changed += mw.col.tags.rename("#BCM::Ethics", "#BCM::Term_4::Ethics").count
    num_changed += mw.col.tags.rename("#BCM::Psych", "#BCM::Term_4::Psych").count
    num_changed += mw.col.tags.rename("#BCM::Neuro", "#BCM::Term_4::Neuro").count
    if num_changed > 0:
        showInfo("Renamed tags")
    else:
        showInfo("No tags to rename")

# create a new menu item, "test"
action1 = QAction("Move To AnKing", mw)
# set it to call testFunction when it's clicked
qconnect(action1.triggered, move_to_anking)
# and add it to the tools menu
mw.form.menuTools.addAction(action1)


# create a new menu item, "test"
action2 = QAction("Move To HassAnki", mw)
# set it to call testFunction when it's clicked
qconnect(action2.triggered, move_to_hassanki)
# and add it to the tools menu
mw.form.menuTools.addAction(action2)

# create a new menu item, "test"
action3 = QAction("Rename Tags", mw)
# set it to call testFunction when it's clicked
qconnect(action3.triggered, rename_tags)
# and add it to the tools menu
mw.form.menuTools.addAction(action3)