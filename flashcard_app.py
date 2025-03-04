import json
import random
import os
from datetime import datetime, date, timedelta

BASE_FILE = "base.json"
RESULTS_FILE = "results.json"
DUE_INTERVAL_DAYS = 3  # a card is due if last studied >= 3 days ago

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding {filename}. Make sure it contains valid JSON.")
                return None
    else:
        print(f"{filename} does not exist.")
        return None

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_last_study_date(card, results):
    """Return the most recent study date for the card (as a date object) or None if not found."""
    matching = [r for r in results if r.get("front") == card.get("front") and r.get("back") == card.get("back")]
    if not matching:
        return None
    # Assuming timestamp is stored in 'YYYY-MM-DD' format.
    latest_str = max(r["timestamp"] for r in matching)
    return datetime.strptime(latest_str, "%Y-%m-%d").date()

def due_flashcards(base, results):
    today = date.today()
    due = []
    for card in base:
        last_date = get_last_study_date(card, results)
        if last_date is None:
            due.append(card)
        else:
            # Check if the card is due (if last studied >= DUE_INTERVAL_DAYS ago)
            if (today - last_date) >= timedelta(days=DUE_INTERVAL_DAYS):
                due.append(card)
    return due

def run_session():
    base = load_json(BASE_FILE)
    if base is None:
        return

    results = load_json(RESULTS_FILE)
    if results is None:
        results = []

    # Determine due flashcards based on spaced repetition rule.
    due_cards = due_flashcards(base, results)
    if not due_cards:
        print("No cards are due for study today. Great job!")
        return

    print(f"{len(due_cards)} card(s) are due for study.\n")

    # Shuffle due cards for the session.
    random.shuffle(due_cards)
    session_results = []  # store new session results here

    i = 0
    while i < len(due_cards):
        card = due_cards[i]
        showing_front = True
        while True:
            print(f"\nCard {i+1} of {len(due_cards)}")
            if showing_front:
                print("Question: " + card["front"])
            else:
                print("Answer: " + card["back"])
            print("\nCommands: [f]lip, [p]ass, [d]fail, [s]kip, [q]uit session")
            choice = input("Your choice: ").strip().lower()
            if choice == "f":
                showing_front = not showing_front
            elif choice == "p":
                # record pass
                session_results.append({
                    "front": card["front"],
                    "back": card["back"],
                    "result": "pass",
                    "timestamp": date.today().strftime("%Y-%m-%d")
                })
                print("Recorded PASS.")
                break
            elif choice == "d":
                # record fail
                session_results.append({
                    "front": card["front"],
                    "back": card["back"],
                    "result": "fail",
                    "timestamp": date.today().strftime("%Y-%m-%d")
                })
                print("Recorded FAIL.")
                break
            elif choice == "s":
                # Skip: push card to end of list to be reviewed again.
                due_cards.append(due_cards.pop(i))
                print("Card skipped. It will come up later.")
                # Do not increment i so that we reprocess the new card at index i.
                continue
            elif choice == "q":
                print("Quitting session early.")
                i = len(due_cards)  # exit outer loop
                break
            else:
                print("Invalid command. Please try again.")
        i += 1

    # Append new session results to the overall results.
    if session_results:
        results.extend(session_results)
        save_json(RESULTS_FILE, results)
        print(f"\nSession complete. {len(session_results)} result(s) recorded.")
    else:
        print("\nNo results recorded this session.")

if __name__ == "__main__":
    run_session()
