import re
from aqt.utils import showInfo, qconnect
from aqt.qt import QAction
from aqt import mw, gui_hooks

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
    try:
        rename_fn = mw.col.tags.rename
    except AttributeError:
        rename_fn = mw.col.tags.rename_tag

    num_changed += rename_fn("#BCM::Pharmacology", "#BCM::Term_3::Pharmacology").count
    num_changed += rename_fn("#BCM::IPBD", "#BCM::Term_3::IPBD").count
    num_changed += rename_fn("#BCM::Anatomy", "#BCM::Term_3::Anatomy").count
    num_changed += rename_fn("#BCM::Infectious_Disease", "#BCM::Term_4::Infectious_Disease").count
    num_changed += rename_fn("#BCM::Ethics", "#BCM::Term_4::Ethics").count
    num_changed += rename_fn("#BCM::Psych", "#BCM::Term_4::Psych").count
    num_changed += rename_fn("#BCM::Neuro", "#BCM::Term_4::Neuro").count
    num_changed += rename_fn("#BCM::Term_6", "#BCM::Term_6A").count
    num_changed += rename_fn("#BCM::Term_7", "#BCM::Term_6B").count

    changes_made = False
    t6a_deck = mw.col.decks.by_name("HassAnki::Term 6")
    if t6a_deck is not None:
        t6a_deck["name"] = "HassAnki::Term 6A"
        mw.col.decks.save(t6a_deck)
        changes_made = True
    t6b_deck = mw.col.decks.by_name("HassAnki::Term 7")
    if t6b_deck is not None:
        t6b_deck["name"] = "HassAnki::Term 6B"
        mw.col.decks.save(t6b_deck)
        changes_made = True

    if num_changed > 0 or changes_made:
        showInfo("Renamed tags")
    else:
        showInfo("No tags to rename")

def add_dialog_option(menu, deck_id):
    def move_to_deck():
        deck = mw.col.decks.get(deck_id)
        if deck['name'].startswith('HassAnki'):
            tag_name = deck['name'].replace('HassAnki', '#BCM').replace(' ', '_')
            cids = mw.col.find_cards('tag:'+tag_name)
            if len(cids) > 0:
                num_moved = 0
                for cid in cids:
                    card = mw.col.get_card(cid)
                    if card.did != deck_id:
                        num_moved += 1
                        card.did = deck_id
                    card.flush()
                showInfo(f"Moved {num_moved} cards to {deck['name']}")
            else:
                showInfo('Could not find any cards. Check that the deck has the same name as the tag')
                return
        else:
            showInfo("Deck must be in HassAnki")
            return
    
    action4 = QAction("Move cards to deck", mw)
    qconnect(action4.triggered, move_to_deck)
    menu.addAction(action4)


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

gui_hooks.deck_browser_will_show_options_menu.append(add_dialog_option)