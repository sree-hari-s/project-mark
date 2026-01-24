# Project Mark – RPG Dice Strategy Game

**Project Mark** is a turn-based RPG dice strategy game where risk, timing, and restraint decide victory.

Each round, one player becomes the **Captain** and sets **The Mark** by rolling a powerful trio of dice: **d6, d12, and d20**. Every other player must chase that number — but go too far, and you’re **BUSTED**.

Simple to learn, tense to play, and built for expansion, Project Mark blends luck with decision-making in every roll.

---

## 🎮 Gameplay Overview

Project Mark is played over multiple rounds. In each round:

- One player is designated as the **Captain**
- The Captain sets **The Mark** by rolling:
  - d6 + d12 + d20
- All other players take turns attempting to reach or get as close as possible to The Mark **without exceeding it**

Each decision matters. Roll too much, and you lose everything for the round. Stop too early, and someone else might edge past you.

---

## ⚓ Core Mechanics

- Each player has access to **three dice** per round:
  - d6
  - d12
  - d20
- Each die can be used **only once per round**
- Dice can be rolled in **any order**
- Players may **end their turn early** to avoid busting
- If a player’s total **exceeds The Mark**, they are **BUSTED**
  - A busted player’s round score counts as **0**

---

## 🏆 Scoring System

At the end of each round:

- **Exact match with The Mark** → **2 points**
- **Closest score without exceeding** → **1 point**
- **All players bust** → **No points awarded**

Points accumulate across rounds.

---

## 🔁 Game Structure

- Default game length: **3 rounds** (configurable)
- Round 1 Captain is chosen randomly
- In later rounds, the **previous round’s winner becomes the Captain**
- Turn order always starts from the player to the Captain’s left
- After all rounds are complete, total points decide the winner

### ⚔️ Sudden Death
If multiple players are tied for first place:
- A **sudden-death d20 roll-off** is triggered
- Highest roll wins the game

---

## 🎲 Why Project Mark?

- Easy-to-understand rules
- High tension with every roll
- Encourages calculated risk and strategic restraint
- Scales well from casual play to competitive sessions
- Designed to be extensible with new mechanics and modes

**Project Mark** is not about rolling the highest number.  
It’s about knowing **when to stop**.

---

## 🖥️ Current Implementation

- Built with **Python + Tkinter**
- Local multiplayer
- Visual turn-based interface
- Full round logging
- Configurable number of rounds
- Sudden-death resolution for ties

Run the game using:

```bash
python project_mark.py
