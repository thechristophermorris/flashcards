import tkinter as tk
from tkinter import messagebox
import json
import random
import os
from datetime import datetime, date, timedelta

# Filenames for the base flashcards and results.
BASE_FILE = "base.json"
RESULTS_FILE = "results.json"
DUE_INTERVAL_DAYS = 3  # A card is due if it hasn't been studied in the past 3 days.

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("Error", f"Error decoding {filename}.")
                return None
    else:
        messagebox.showerror("Error", f"{filename} does not exist.")
        return None

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_last_study_date(card, results):
    """Return the most recent study date for the card as a date object, or None if never studied."""
    matching = [
        r for r in results
        if r.get("front") == card.get("front") and r.get("back") == card.get("back")
    ]
    if not matching:
        return None
    # Assume timestamp is stored as "YYYY-MM-DD"
    latest_str = max(r["timestamp"] for r in matching)
    return datetime.strptime(latest_str, "%Y-%m-%d").date()

def get_due_cards(base, results):
    """Return a list of cards that are due for study."""
    due = []
    today = date.today()
    for card in base:
        last_date = get_last_study_date(card, results)
        if last_date is None or (today - last_date) >= timedelta(days=DUE_INTERVAL_DAYS):
            due.append(card)
    return due

class FlashcardApp:
    def __init__(self, master):
        self.master = master
        master.title("Flashcard App")

        # Load data from JSON files.
        self.base = load_json(BASE_FILE)
        if self.base is None:
            self.base = []
        self.results = load_json(RESULTS_FILE)
        if self.results is None:
            self.results = []

        # Compute due cards using the spaced repetition rule.
        self.due_cards = get_due_cards(self.base, self.results)
        random.shuffle(self.due_cards)
        self.current_index = 0
        self.showing_front = True

        # Create GUI elements.
        self.card_label = tk.Label(master, text="", wraplength=500, font=("Helvetica", 18), justify="center")
        self.card_label.pack(pady=20)

        self.status_label = tk.Label(master, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        # Create a frame for the buttons.
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        # Create buttons.
        self.pass_button = tk.Button(self.button_frame, text="Pass", width=10, command=self.pass_card)
        self.pass_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.fail_button = tk.Button(self.button_frame, text="Fail", width=10, command=self.fail_card)
        self.fail_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.flip_button = tk.Button(self.button_frame, text="Flip", width=10, command=self.flip_card)
        self.flip_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.skip_button = tk.Button(self.button_frame, text="Skip", width=10, command=self.skip_card)
        self.skip_button.grid(row=0, column=3, padx=5, pady=5)
        
        self.randomize_button = tk.Button(self.button_frame, text="Randomize", width=10, command=self.randomize_deck)
        self.randomize_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.startover_button = tk.Button(self.button_frame, text="Start Over", width=10, command=self.start_over)
        self.startover_button.grid(row=1, column=1, padx=5, pady=5)

        self.update_card_display()

    def update_card_display(self):
        if self.current_index < len(self.due_cards):
            card = self.due_cards[self.current_index]
            text = card["front"] if self.showing_front else card["back"]
            self.card_label.config(text=text)
            self.status_label.config(text=f"Card {self.current_index + 1} of {len(self.due_cards)}")
        else:
            self.card_label.config(text="All due cards have been reviewed!")
            self.status_label.config(text="")

    def record_result(self, result):
        if self.current_index >= len(self.due_cards):
            return
        card = self.due_cards[self.current_index]
        new_result = {
            "front": card["front"],
            "back": card["back"],
            "result": result,
            "timestamp": date.today().strftime("%Y-%m-%d")
        }
        self.results.append(new_result)
        save_json(RESULTS_FILE, self.results)
        self.current_index += 1
        self.showing_front = True
        self.update_card_display()

    def pass_card(self):
        self.record_result("pass")

    def fail_card(self):
        self.record_result("fail")

    def flip_card(self):
        self.showing_front = not self.showing_front
        self.update_card_display()

    def skip_card(self):
        if self.current_index < len(self.due_cards):
            # Move the current card to the end of the list.
            card = self.due_cards.pop(self.current_index)
            self.due_cards.append(card)
            self.showing_front = True
            self.update_card_display()

    def randomize_deck(self):
        random.shuffle(self.due_cards)
        self.current_index = 0
        self.showing_front = True
        self.update_card_display()

    def start_over(self):
        # Recompute due cards from the current base and results.
        self.due_cards = get_due_cards(self.base, self.results)
        random.shuffle(self.due_cards)
        self.current_index = 0
        self.showing_front = True
        self.update_card_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
