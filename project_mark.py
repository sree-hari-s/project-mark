"""
Kraken - RPG Dice Game (Tkinter)
File: kraken_game.py

Fixed and improved by assistant:
- Removed syntax errors (unmatched parenthesis, wrong widget parent, duplicate messagebox call).
- Top UI now shows "Round Points" for the current player instead of live total.
- Players now have a persistent `points` attribute (accumulated across rounds).
- end_round awards: 2 points if player exactly equals the Mark, 1 point if closest without exceeding.
- After 3 rounds the overall winner(s) are logged; if tied, a sudden-death d20 roll-off decides the winner.
- Clean, tested control flow for enabling/disabling dice per player, and proper UI updates.

Usage: python kraken_game.py
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import functools

# ------------------ Game Data Structures ------------------
class Player:
    def __init__(self, name):
        self.name = name
        self.total = 0            # round total
        self.busted = False
        self.used_dice = set()    # 'd6','d12','d20' used this round
        self.points = 0           # cumulative round points

    def reset_for_round(self):
        self.total = 0
        self.busted = False
        self.used_dice = set()

    def has_used(self, die_label):
        return die_label in self.used_dice

    def mark_used(self, die_label):
        self.used_dice.add(die_label)

    def is_done(self):
        # done if busted or all three dice used
        return self.busted or len(self.used_dice) >= 3

# ------------------ Main App ------------------
class KrakenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kraken - RPG Dice Game")
        self.configure(bg="#0b0b0b")
        self.geometry("960x640")

        # Game config
        self.num_rounds = 3
        self.current_round = 0
        self.players = []
        self.captain_idx = None
        self.mark = None
        self.turn_order = []
        self.current_turn_idx = 0

        # Build UI
        self._build_header()
        self._build_player_area()
        self._build_center_log()
        self._build_controls()
        self._build_menu()

        # Start setup shortly after launch
        self.after(100, self.start_setup)

    # ------------------ UI Building ------------------
    def _build_header(self):
        header = tk.Frame(self, bg="#0b0b0b")
        header.pack(fill=tk.X, padx=8, pady=8)

        self.lbl_round = tk.Label(header, text="Round: -/{}".format(self.num_rounds), fg="#7CFC00",
                                  bg="#0b0b0b", font=("Consolas", 14, "bold"))
        self.lbl_round.pack(side=tk.LEFT)

        self.lbl_mark = tk.Label(header, text="Mark: -", fg="#39FF14", bg="#0b0b0b", font=("Consolas", 14))
        self.lbl_mark.pack(side=tk.LEFT, padx=20)

        self.lbl_captain = tk.Label(header, text="Captain: -", fg="#66FFCC", bg="#0b0b0b", font=("Consolas", 14))
        self.lbl_captain.pack(side=tk.LEFT, padx=20)

        # Right side: show Round Points for current player (user chose Option B)
        self.lbl_round_points = tk.Label(header, text="Round Points: 0", fg="#E0FFE0", bg="#0b0b0b",
                                         font=("Consolas", 14))
        self.lbl_round_points.pack(side=tk.RIGHT, padx=12)

    def _build_player_area(self):
        frame = tk.Frame(self, bg="#0b0b0b")
        frame.pack(fill=tk.X, padx=8)
        self.player_cards = tk.Frame(frame, bg="#0b0b0b")
        self.player_cards.pack(side=tk.LEFT, fill=tk.X)

    def _build_center_log(self):
        center = tk.Frame(self, bg="#0b0b0b")
        center.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        log_frame = tk.Frame(center, bg="#111")
        log_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.txt_log = tk.Text(log_frame, bg="#050505", fg="#7CFC00", insertbackground="#7CFC00",
                                font=("Consolas", 11), state=tk.DISABLED)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        right = tk.Frame(center, bg="#0b0b0b", width=260)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbl_turn = tk.Label(right, text="Current Turn: -", fg="#E0FFE0", bg="#0b0b0b",
                                 font=("Consolas", 12))
        self.lbl_turn.pack(pady=6)

        # We no longer show live player 'total' at top; show points on header instead.
        self.lbl_status = tk.Label(right, text="Status: -", fg="#E0FFE0", bg="#0b0b0b",
                                   font=("Consolas", 12))
        self.lbl_status.pack(pady=6)

    def _build_controls(self):
        controls = tk.Frame(self, bg="#0b0b0b")
        controls.pack(fill=tk.X, padx=8, pady=6)

        dice_frame = tk.Frame(controls, bg="#0b0b0b")
        dice_frame.pack(side=tk.LEFT)

        # Buttons for the three dice allowed
        self.btn_d6 = tk.Button(dice_frame, text="d6", width=6, command=functools.partial(self.player_roll, 6))
        self.btn_d6.pack(side=tk.LEFT, padx=4)
        self.btn_d12 = tk.Button(dice_frame, text="d12", width=6, command=functools.partial(self.player_roll, 12))
        self.btn_d12.pack(side=tk.LEFT, padx=4)
        self.btn_d20 = tk.Button(dice_frame, text="d20", width=6, command=functools.partial(self.player_roll, 20))
        self.btn_d20.pack(side=tk.LEFT, padx=4)

        action_frame = tk.Frame(controls, bg="#0b0b0b")
        action_frame.pack(side=tk.RIGHT)

        # Next Turn button - player can end turn early by pressing this
        self.btn_next = tk.Button(action_frame, text="Next Turn", width=12, command=self.next_turn)
        self.btn_next.pack(side=tk.RIGHT, padx=8)

        # Initially disabled until game starts
        for w in (self.btn_d6, self.btn_d12, self.btn_d20, self.btn_next):
            w.config(state=tk.DISABLED)

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.start_setup)
        game_menu.add_command(label="Set Rounds...", command=self.set_rounds)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Rules", command=self.show_rules)

    # ------------------ Setup / Game Flow ------------------
    def start_setup(self):
        # Reset state
        self.players = []
        self.current_round = 0
        self.mark = None
        self.captain_idx = None
        self.turn_order = []
        self.current_turn_idx = 0
        self.clear_log()
        self._refresh_player_cards()

        # Ask num players
        try:
            n = simpledialog.askinteger("Players", "Enter number of players (min 2):", minvalue=2)
        except Exception:
            return
        if not n or n < 2:
            messagebox.showinfo("Info", "Game requires at least 2 players.")
            return

        for i in range(n):
            name = simpledialog.askstring("Player Name", f"Enter name for Player {i+1}:", initialvalue=f"Player {i+1}")
            if not name:
                name = f"Player {i+1}"
            p = Player(name)
            p.points = 0
            self.players.append(p)

        self._log(f"Created {len(self.players)} players.")
        self._refresh_player_cards()

        # Choose captain for round 1 randomly
        self.captain_idx = random.randrange(len(self.players))
        self._log(f"Captain for Round 1 chosen randomly: {self.players[self.captain_idx].name}")
        self.start_round()

    def set_rounds(self):
        r = simpledialog.askinteger("Rounds", "Enter number of rounds (1-10):", minvalue=1, maxvalue=10, initialvalue=self.num_rounds)
        if r:
            self.num_rounds = r
            self.lbl_round.config(text=f"Round: {self.current_round}/{self.num_rounds}")

    def show_rules(self):
        rules = (
            "Rules summary:\n"
            "1. Captain sets 'The Mark' by rolling d20 + d12 + d6.\n"
            "2. Players may use each of d6, d12, d20 once per their turn (they can pick order).\n"
            "3. After a roll the die used becomes disabled for that player in this round.\n"
            "4. Turn ends when player used all three dice, busts, or presses Next Turn.\n"
            "5. If a player exceeds The Mark, they are BUSTED and their round total counts as 0.\n"
            "6. Highest total <= Mark wins the round. Closest gets 1 point; exact Match gets 2 points.\n"
            "7. Round 1 captain random; later rounds captain = previous round winner.\n"
        )
        messagebox.showinfo("Rules", rules)

    # ------------------ Round Flow ------------------
    def start_round(self):
        self.current_round += 1
        if self.current_round > self.num_rounds:
            self._log("All rounds complete.")
            self._end_game()
            return

        self._log(f"\n--- Starting Round {self.current_round} ---")
        # Reset players for round
        for p in self.players:
            p.reset_for_round()
        self.mark = None
        self.lbl_mark.config(text=f"Mark: -")

        self.lbl_round.config(text=f"Round: {self.current_round}/{self.num_rounds}")
        self.lbl_captain.config(text=f"Captain: {self.players[self.captain_idx].name}")

        # Captain sets the mark
        self.set_mark_by_captain()

    def set_mark_by_captain(self):
        # Captain rolls d20 + d12 + d6
        v20 = random.randint(1, 20)
        v12 = random.randint(1, 12)
        v6 = random.randint(1, 6)
        self.mark = v20 + v12 + v6
        self.lbl_mark.config(text=f"Mark: {self.mark}  ( {v20} + {v12} + {v6} )")
        self._log(f"Captain {self.players[self.captain_idx].name} sets The Mark: {self.mark} (rolled {v20} + {v12} + {v6})")

        # Build turn order starting from player to captain's left
        n = len(self.players)
        order = []
        for i in range(1, n+1):
            order.append((self.captain_idx + i) % n)
        self.turn_order = order
        self.current_turn_idx = 0
        self._log("Turn order: " + ", ".join(self.players[i].name for i in self.turn_order))

        # Enable controls for first player
        self.update_ui_for_turn()
        self._enable_controls_for_current_player()

    def update_ui_for_turn(self):
        if self.current_turn_idx >= len(self.turn_order):
            # End of round
            self.end_round()
            return

        idx = self.turn_order[self.current_turn_idx]
        player = self.players[idx]
        self.lbl_turn.config(text=f"Current Turn: {player.name}")
        # show current player's cumulative points in header
        self.lbl_round_points.config(text=f"Round Points: {player.points}")
        status = "BUSTED" if player.busted else ("DONE" if player.is_done() else "ACTIVE")
        self.lbl_status.config(text=f"Status: {status}")
        self._refresh_player_cards()

    def _enable_controls_for_current_player(self):
        # enable dice buttons that the current player hasn't used yet
        if self.current_turn_idx >= len(self.turn_order):
            return
        idx = self.turn_order[self.current_turn_idx]
        player = self.players[idx]

        # map die sides to buttons and labels
        die_map = {6: (self.btn_d6, 'd6'), 12: (self.btn_d12, 'd12'), 20: (self.btn_d20, 'd20')}
        for sides, (btn, label) in die_map.items():
            if player.has_used(label) or player.busted:
                btn.config(state=tk.DISABLED)
            else:
                btn.config(state=tk.NORMAL)
        # Next turn always available so player can finish early
        self.btn_next.config(state=tk.NORMAL)

    def _disable_all_controls(self):
        for w in (self.btn_d6, self.btn_d12, self.btn_d20, self.btn_next):
            w.config(state=tk.DISABLED)

    # ------------------ Player Actions ------------------
    def player_roll(self, sides):
        if self.current_turn_idx >= len(self.turn_order):
            return
        idx = self.turn_order[self.current_turn_idx]
        player = self.players[idx]

        die_label = f'd{str(sides)}'
        if player.has_used(die_label) or player.busted:
            self._log(f"{player.name} cannot use {die_label} (already used or busted).")
            return

        roll = random.randint(1, sides)
        player.total += roll
        player.mark_used(die_label)

        self._log(f"{player.name} rolls {die_label} -> {roll}")
        self._log(f"{player.name} total is now {player.total} (Mark: {self.mark})")

        if self.mark is not None and player.total > self.mark:
            player.busted = True
            self._log(f"{player.name} has EXCEEDED The Mark and is BUSTED. Their score will count as 0 for this round.")

        # Update UI and either end turn if done or allow further rolls
        self.update_ui_for_turn()
        if player.is_done():
            self._log(f"{player.name} has used all dice or busted — ending their turn.")
            # disable current player's dice and automatically advance
            self._disable_all_controls()
            # advance after a short delay so user sees result
            self.after(400, self.next_turn)
        else:
            # enable/disable buttons according to which dice remain
            self._enable_controls_for_current_player()

    def next_turn(self):
        # Move to next player in turn order
        self.current_turn_idx += 1
        if self.current_turn_idx >= len(self.turn_order):
            self.end_round()
            return
        self.update_ui_for_turn()
        self._enable_controls_for_current_player()

    # ------------------ Round End & Scoring ------------------
    def end_round(self):
        self._log("--- Round Complete: Calculating results ---")
        self._disable_all_controls()

        # Determine winner(s): highest total <= mark. Busted players count as 0.
        best_score = -1
        winners = []
        for p in self.players:
            score = 0 if p.busted else p.total
            self._log(f"{p.name}: {'BUSTED' if p.busted else score}")
            if score <= (self.mark if self.mark is not None else 0):
                if score > best_score:
                    best_score = score
                    winners = [p]
                elif score == best_score:
                    winners.append(p)

        # Award points
        # If all players busted (all scores > mark), no one gets points.
        any_valid = any((not p.busted) and p.total <= self.mark for p in self.players)
        if not any_valid:
            self._log("All players exceeded The Mark. No points awarded this round.")
        else:
            for p in self.players:
                if p in winners:
                    if p.total == self.mark:
                        p.points += 2
                    else:
                        p.points += 1

        for p in self.players:
            self._log(f"{p.name}: points={p.points}")

        # Decide captain for next round: choose winner (first) if exists
        if winners:
            next_captain_idx = self.players.index(winners[0])
            self._log(f"{winners[0].name} will be Captain for the next round.")
            self.captain_idx = next_captain_idx

        # If more rounds remain start next, else end game
        if self.current_round < self.num_rounds:
            # small pause so user can read results
            self.after(800, self.start_round)
        else:
            self._log("All rounds finished.")
            self._end_game()

    def _end_game(self):
        # Determine final winner by points
        max_pts = max(p.points for p in self.players)
        tied_players = [p for p in self.players if p.points == max_pts]

        if len(tied_players) == 1:
            winner = tied_players[0]
            self._log(f"=== GAME OVER ===\nWinner: {winner.name} with {winner.points} points!")
        else:
            # Sudden death roll-off among tied players: single d20 roll
            names = ", ".join(p.name for p in tied_players)
            self._log(f"Tie for first place between: {names}. Starting sudden-death d20 roll-off...")
            results = {}
            for p in tied_players:
                roll = random.randint(1, 20)
                results[p] = roll
                self._log(f"Sudden Death - {p.name} rolls d20 → {roll}")
            winner = max(results, key=results.get)
            self._log(f"Sudden Death Winner: {winner.name} with roll {results[winner]}")

        # Final scores summary
        self._log("Final scores:")
        for p in self.players:
            self._log(f"{p.name}: {p.points} points")

        messagebox.showinfo("Game Over", "All rounds finished. See log for details.")

    # ------------------ Helpers ------------------
    def _log(self, text):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.insert(tk.END, text + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state=tk.DISABLED)

    def clear_log(self):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.config(state=tk.DISABLED)

    def _refresh_player_cards(self):
        # Clear existing
        for child in self.player_cards.winfo_children():
            child.destroy()

        for i, p in enumerate(self.players):
            card = tk.Frame(self.player_cards, bg="#0b0b0b", bd=1, relief=tk.RIDGE, padx=8, pady=6)
            card.pack(side=tk.LEFT, padx=6, pady=6)
            lbl = tk.Label(card, text=p.name, fg="#E0FFE0", bg="#0b0b0b", font=("Consolas", 11, "bold"))
            lbl.pack()
            tot = tk.Label(card, text=f"Total: {p.total}", fg="#C0FFC0", bg="#0b0b0b")
            tot.pack()
            status_text = "BUSTED" if p.busted else ("DONE" if p.is_done() else "ACTIVE")
            stat = tk.Label(card, text=status_text, fg="#C0FFC0", bg="#0b0b0b")
            stat.pack()
            pts = tk.Label(card, text=f"Points: {p.points}", fg="#FFD880", bg="#0b0b0b")
            pts.pack()


if __name__ == "__main__":
    app = KrakenApp()
    app.mainloop()
