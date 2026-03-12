"""
Project Mark - Web Edition (Streamlit)
=======================================
A turn-based dice strategy game playable in the browser.

Run with: streamlit run app.py
"""

import random
import streamlit as st

# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Project Mark",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Player & Game logic (pure Python, no UI)
# ---------------------------------------------------------------------------


class Player:
    """Represents a single player in the game."""

    def __init__(self, name):
        self.name = name
        self.total = 0  # Running total for the current round
        self.points = 0  # Accumulated game points
        self.busted = False  # Exceeded The Mark this round
        self.done = False  # Finished their turn this round
        self.used_dice = set(
        )  # Die sizes already rolled this round: {6, 12, 20}

    def reset_round(self):
        """Reset per-round state for a new round."""
        self.total = 0
        self.busted = False
        self.done = False
        self.used_dice = set()

    @property
    def status(self):
        if self.busted:
            return "💥 Busted"
        if self.done:
            return "✅ Done"
        return "🎲 Active"


class Game:
    """Pure game logic — no UI references."""

    def __init__(self, player_names, num_rounds=3):
        self.players = [Player(n) for n in player_names]
        self.num_rounds = num_rounds
        self.current_round = 1
        self.captain_index = random.randint(0, len(self.players) - 1)
        self.mark = 0
        self.turn_order = []  # Indices of non-captain players in turn order
        self.turn_index = 0  # Current position within turn_order
        self.phase = "captain"  # captain | playing | scoring | gameover
        self._build_turn_order()

    def _build_turn_order(self):
        """Turn order starts from the player to the captain's left, captain goes last."""
        n = len(self.players)
        self.turn_order = [(self.captain_index + 1 + i) % n for i in range(n)]
        self.turn_index = 0

    @property
    def captain(self):
        return self.players[self.captain_index]

    @property
    def current_player(self):
        if self.phase != "playing":
            return None
        if self.turn_index >= len(self.turn_order):
            return None
        return self.players[self.turn_order[self.turn_index]]

    def captain_roll_mark(self):
        """Captain rolls d20+d12+d6 to set The Mark. Returns roll breakdown."""
        d20 = random.randint(1, 20)
        d12 = random.randint(1, 12)
        d6 = random.randint(1, 6)
        self.mark = d20 + d12 + d6
        self.phase = "playing"
        return {"d20": d20, "d12": d12, "d6": d6, "total": self.mark}

    def player_roll(self, sides):
        """
        Roll a die for the current player.
        Returns (roll_value, busted) or (None, False) if die already used.
        """
        player = self.current_player
        if player is None or sides in player.used_dice:
            return None, False

        roll = random.randint(1, sides)
        player.used_dice.add(sides)
        player.total += roll

        busted = player.total > self.mark
        if busted:
            player.busted = True
            player.done = True

        return roll, busted

    def end_current_turn(self):
        """Mark current player done and advance the turn pointer."""
        player = self.current_player
        if player is not None:
            player.done = True
        self.turn_index += 1
        if self.turn_index >= len(self.turn_order):
            self.phase = "scoring"

    def calculate_round_scores(self):
        """
        Award points and return a summary dict:
          - all_busted: bool
          - exact_match: list of player names
          - closest: list of player names
        """
        result = {"all_busted": False, "exact_match": [], "closest": []}
        valid = [
            self.players[i] for i in self.turn_order
            if not self.players[i].busted
        ]

        if not valid:
            result["all_busted"] = True
            return result

        exact = [p for p in valid if p.total == self.mark]
        if exact:
            for p in exact:
                p.points += 2
                result["exact_match"].append(p.name)
            return result

        best = max(p.total for p in valid)
        closest = [p for p in valid if p.total == best]
        for p in closest:
            p.points += 1
            result["closest"].append(p.name)
        return result

    def set_next_captain(self):
        """Winner of the round becomes next captain. Resets all players."""
        valid = [
            self.players[i] for i in self.turn_order
            if not self.players[i].busted
        ]
        if valid:
            winner = max(valid, key=lambda p: p.total)
            self.captain_index = self.players.index(winner)
        for p in self.players:
            p.reset_round()
        self.current_round += 1
        self._build_turn_order()
        self.phase = "captain"
        self.mark = 0

    def get_game_winners(self):
        """Return list of players tied for first place."""
        max_pts = max(p.points for p in self.players)
        return [p for p in self.players if p.points == max_pts]

    def sudden_death_roll(self, tied_players):
        """Each tied player rolls d20. Returns rolls dict and winner list."""
        rolls = {p.name: random.randint(1, 20) for p in tied_players}
        best = max(rolls.values())
        winners = [p for p in tied_players if rolls[p.name] == best]
        return rolls, winners


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------


def init_state():
    """Initialize session_state keys that must always exist."""
    defaults = {
        "phase":
        "setup",  # setup | captain | playing | scoring | sudden_death | gameover
        "game": None,
        "log": [],  # List of log message strings
        "last_captain_roll": None,  # Dict from captain_roll_mark()
        "last_roll": None,  # (sides, value) of most recent player roll
        "round_result": None,  # Dict from calculate_round_scores()
        "sd_rolls": None,  # Sudden-death roll results
        "sd_tied": None,  # Players still tied after a sudden-death round
        "final_winner": None,  # Winner player name
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def log(msg):
    """Append a message to the game log."""
    st.session_state.log.append(msg)


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------


def render_player_table(game):
    """Render the scoreboard showing all players."""
    current = game.current_player

    rows = []
    for player in game.players:
        is_captain = (player == game.captain)
        is_current = (player == current and game.phase == "playing")

        name = player.name
        if is_captain:
            name = f"⚓ {name}"
        if is_current:
            name = f"**{name}**"

        rows.append({
            "Player": name,
            "Round Total": player.total,
            "Status": player.status,
            "Points": player.points,
        })

    st.table(rows)


def render_log():
    """Render the scrollable game log."""
    if st.session_state.log:
        log_text = "\n".join(
            st.session_state.log[-60:])  # Show last 60 entries
        st.text_area("Game Log",
                     value=log_text,
                     height=260,
                     disabled=True,
                     label_visibility="visible")


# ---------------------------------------------------------------------------
# Phase renderers
# ---------------------------------------------------------------------------


def render_setup():
    """Setup screen: collect player names and round count."""
    st.title("🎲 Project Mark")
    st.markdown(
        "*A turn-based dice strategy game — reach The Mark without going over!*"
    )
    st.divider()

    with st.form("setup_form"):
        num_rounds = st.number_input("Number of Rounds",
                                     min_value=1,
                                     max_value=10,
                                     value=3,
                                     step=1)
        st.markdown("**Player Names** (2 required, up to 8)")

        cols = st.columns(2)
        name_inputs = []
        for i in range(8):
            col = cols[i % 2]
            label = f"Player {i+1}" + (" *" if i < 2 else " (optional)")
            default = f"Player {i+1}" if i < 2 else ""
            name_inputs.append(
                col.text_input(label, value=default, key=f"name_{i}"))

        submitted = st.form_submit_button("🚀 Start Game",
                                          use_container_width=True)

    if submitted:
        names = []
        seen = set()
        error = None
        for n in name_inputs:
            n = n.strip()
            if n:
                if n.lower() in seen:
                    error = f'Duplicate name "{n}" — please use unique names.'
                    break
                seen.add(n.lower())
                names.append(n)

        if error:
            st.error(error)
        elif len(names) < 2:
            st.error("Please enter at least 2 player names.")
        else:
            game = Game(names, num_rounds=int(num_rounds))
            st.session_state.game = game
            st.session_state.phase = "captain"
            st.session_state.log = []
            log("=== Welcome to Project Mark! ===")
            log(f"Players: {', '.join(names)}")
            log(f"Rounds to play: {num_rounds}")
            log(f"\n--- Round 1 of {num_rounds} ---")
            log(f"Captain: {game.captain.name}")
            st.rerun()


def render_captain_phase(game):
    """Captain phase: show info and let captain roll for The Mark."""
    st.header(f"🎲 Round {game.current_round} of {game.num_rounds}")
    st.subheader(f"⚓ Captain: {game.captain.name}")
    st.info(
        f"The Captain rolls **d20 + d12 + d6** to set **The Mark** for this round."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        render_player_table(game)
    with col2:
        render_log()

    st.divider()
    if st.button(f"🎲 {game.captain.name}: Roll for The Mark!",
                 use_container_width=True,
                 type="primary"):
        result = game.captain_roll_mark()
        st.session_state.last_captain_roll = result
        log(f"{game.captain.name} rolls for The Mark: "
            f"d20={result['d20']}, d12={result['d12']}, d6={result['d6']} "
            f"→ THE MARK = {result['total']}")
        st.session_state.phase = "playing"
        # Log first player's turn
        if game.current_player:
            log(f"\n{game.current_player.name}'s turn (target: {game.mark})")
        st.rerun()


def render_playing_phase(game):
    """Player turn phase: dice buttons, current total, end turn."""
    player = game.current_player

    # If somehow we land here with no current player, go to scoring
    if player is None:
        st.session_state.phase = "scoring"
        st.rerun()
        return

    st.header(f"🎲 Round {game.current_round} of {game.num_rounds}")

    # Header metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("The Mark", game.mark)
    m2.metric("Current Player", player.name)
    m3.metric("Your Total", player.total)
    over = player.total - game.mark if player.total > 0 else 0
    m4.metric("Remaining", game.mark - player.total, delta_color="inverse")

    # Show last roll result if any
    if st.session_state.last_roll:
        sides, value = st.session_state.last_roll
        if player.busted:
            st.error(
                f"💥 Rolled d{sides}: **{value}** — Total: **{player.total}** — BUSTED! (exceeded {game.mark})"
            )
        else:
            st.success(
                f"🎲 Rolled d{sides}: **{value}** — Running Total: **{player.total}**"
            )

    col1, col2 = st.columns([2, 1])
    with col1:
        render_player_table(game)
    with col2:
        render_log()

    st.divider()
    st.subheader(f"🎯 {player.name}'s Dice")

    # Dice buttons — disable each after it's been rolled
    dice_cols = st.columns(4)
    d6_used = 6 in player.used_dice
    d12_used = 12 in player.used_dice
    d20_used = 20 in player.used_dice

    with dice_cols[0]:
        if st.button("🎲 Roll d6" + (" ✓" if d6_used else ""),
                     disabled=d6_used or player.busted or player.done,
                     use_container_width=True,
                     key="roll_d6"):
            _do_player_roll(game, 6)

    with dice_cols[1]:
        if st.button("🎲 Roll d12" + (" ✓" if d12_used else ""),
                     disabled=d12_used or player.busted or player.done,
                     use_container_width=True,
                     key="roll_d12"):
            _do_player_roll(game, 12)

    with dice_cols[2]:
        if st.button("🎲 Roll d20" + (" ✓" if d20_used else ""),
                     disabled=d20_used or player.busted or player.done,
                     use_container_width=True,
                     key="roll_d20"):
            _do_player_roll(game, 20)

    with dice_cols[3]:
        if st.button("🛑 End Turn",
                     disabled=player.busted or player.done,
                     use_container_width=True,
                     type="secondary",
                     key="end_turn"):
            _do_end_turn(game)


def _do_player_roll(game, sides):
    """Handle a die roll for the current player."""
    player = game.current_player
    roll, busted = game.player_roll(sides)
    if roll is None:
        return

    st.session_state.last_roll = (sides, roll)
    log(f"  {player.name} rolls d{sides}: {roll} → total = {player.total}")

    if busted:
        log(f"  *** {player.name} BUSTED! ({player.total} > {game.mark}) ***")
        # Auto-advance after bust
        _advance_turn(game)
    elif len(player.used_dice) == 3:
        # All dice used — auto-advance
        log(f"  {player.name} used all dice.")
        _advance_turn(game)
    else:
        st.rerun()


def _do_end_turn(game):
    """Handle End Turn button."""
    player = game.current_player
    if player:
        log(f"  {player.name} ends their turn with total {player.total}.")
    _advance_turn(game)


def _advance_turn(game):
    """End the current turn and move to the next player or scoring."""
    game.end_current_turn()
    st.session_state.last_roll = None

    if game.phase == "scoring":
        st.session_state.phase = "scoring"
    else:
        # Log next player's turn
        next_player = game.current_player
        if next_player:
            log(f"\n{next_player.name}'s turn (target: {game.mark})")

    st.rerun()


def render_scoring_phase(game):
    """Show round results and button to continue."""
    st.header(f"📊 Round {game.current_round} Results")

    # Calculate scores (only once)
    if st.session_state.round_result is None:
        result = game.calculate_round_scores()
        st.session_state.round_result = result

        log(f"\n--- Round {game.current_round} Results ---")
        for i in game.turn_order:
            p = game.players[i]
            if p.busted:
                log(f"  {p.name}: BUSTED — 0 pts this round (total: {p.points})"
                    )
            else:
                log(f"  {p.name}: total={p.total} (total pts: {p.points})")

        if result["all_busted"]:
            log("  All players busted — no points awarded.")
        elif result["exact_match"]:
            log(f"  ✦ EXACT MATCH! {', '.join(result['exact_match'])} scores 2 points!"
                )
        elif result["closest"]:
            log(f"  Closest: {', '.join(result['closest'])} scores 1 point.")

    result = st.session_state.round_result

    # Announce result
    if result["all_busted"]:
        st.warning("💥 All players busted! No points awarded this round.")
    elif result["exact_match"]:
        st.success(
            f"✦ EXACT MATCH! **{', '.join(result['exact_match'])}** scores 2 points!"
        )
    elif result["closest"]:
        st.info(
            f"🏅 Closest to The Mark: **{', '.join(result['closest'])}** scores 1 point."
        )

    st.subheader("Scoreboard")
    col1, col2 = st.columns([2, 1])
    with col1:
        render_player_table(game)
    with col2:
        render_log()

    st.divider()

    is_last_round = (game.current_round >= game.num_rounds)
    btn_label = "🏁 See Final Results" if is_last_round else f"▶ Start Round {game.current_round + 1}"

    if st.button(btn_label, use_container_width=True, type="primary"):
        st.session_state.round_result = None
        st.session_state.last_captain_roll = None

        if is_last_round:
            game.phase = "gameover"
            st.session_state.phase = "gameover"
        else:
            game.set_next_captain()
            st.session_state.phase = "captain"
            log(f"\n--- Round {game.current_round} of {game.num_rounds} ---")
            log(f"Captain: {game.captain.name}")

        st.rerun()


def render_gameover_phase(game):
    """Final results, winner announcement, and optional tie-break."""
    st.header("🏁 Game Over!")

    # Compute final standings
    sorted_players = sorted(game.players, key=lambda p: p.points, reverse=True)
    st.subheader("Final Standings")
    rows = [{
        "Place": i + 1,
        "Player": p.name,
        "Points": p.points
    } for i, p in enumerate(sorted_players)]
    st.table(rows)

    winners = game.get_game_winners()

    if len(winners) == 1:
        # Clear winner
        winner = winners[0]
        st.balloons()
        st.success(f"🏆 **{winner.name.upper()} WINS THE GAME!** 🏆")
        log(f"\n  🏆 {winner.name.upper()} WINS THE GAME! 🏆")
        _render_play_again()

    else:
        # Tie — sudden death
        tied_names = ", ".join(w.name for w in winners)

        if st.session_state.sd_tied is None:
            # First time here — set up for initial sudden death
            st.warning(
                f"**TIE** between {tied_names}! Sudden-death d20 roll-off!")
            log(f"\n  TIE between {tied_names}! Sudden-death roll-off!")
            if st.button("🎲 Roll Sudden-Death d20s!",
                         use_container_width=True,
                         type="primary"):
                st.session_state.sd_tied = winners
                st.rerun()
        else:
            # Roll-off is happening
            tied = st.session_state.sd_tied

            if st.session_state.sd_rolls is None:
                # Perform the roll
                rolls, new_winners = game.sudden_death_roll(tied)
                st.session_state.sd_rolls = rolls

                rolls_text = ", ".join(f"{n}: {r}" for n, r in rolls.items())
                log(f"  Sudden-death d20 — {rolls_text}")

                if len(new_winners) == 1:
                    # We have a winner
                    st.session_state.final_winner = new_winners[0].name
                    log(f"  🏆 {new_winners[0].name.upper()} WINS!")
                else:
                    # Still tied — prep next roll
                    still = ", ".join(w.name for w in new_winners)
                    log(f"  Still tied ({still}) — rolling again!")
                    st.session_state.sd_tied = new_winners
                    st.session_state.sd_rolls = None

                st.rerun()

            else:
                # Show results of the roll
                st.subheader("⚡ Sudden-Death Roll-Off")
                for name, roll in st.session_state.sd_rolls.items():
                    st.write(f"**{name}** rolled: {roll}")

                if st.session_state.final_winner:
                    st.balloons()
                    st.success(
                        f"🏆 **{st.session_state.final_winner.upper()} WINS!** 🏆"
                    )
                    _render_play_again()
                else:
                    still = ", ".join(w.name for w in st.session_state.sd_tied)
                    st.warning(f"Still tied: {still}! Rolling again...")
                    if st.button("🎲 Roll Again!",
                                 use_container_width=True,
                                 type="primary"):
                        st.session_state.sd_rolls = None
                        st.rerun()

    col_spacer, col_log = st.columns([2, 1])
    with col_log:
        render_log()


def _render_play_again():
    """Render the Play Again button."""
    st.divider()
    if st.button("🔄 Play Again", use_container_width=True):
        # Clear all state and restart
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ---------------------------------------------------------------------------
# Main app entry point
# ---------------------------------------------------------------------------


def main():
    init_state()

    phase = st.session_state.phase
    game = st.session_state.game

    if phase == "setup":
        render_setup()

    elif phase == "captain" and game:
        render_captain_phase(game)

    elif phase == "playing" and game:
        render_playing_phase(game)

    elif phase == "scoring" and game:
        render_scoring_phase(game)

    elif phase == "gameover" and game:
        render_gameover_phase(game)

    else:
        # Fallback — reset to setup if state is inconsistent
        st.session_state.phase = "setup"
        st.rerun()


if __name__ == "__main__":
    main()
