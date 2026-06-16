# Dungeon Crawler

A simple roguelike dungeon crawler built with **Python** and **Pygame Zero**.

Explore randomly generated dungeons, battle monsters, collect treasure, level up your character, and descend deeper into the dungeon. Reach Floor 10 to achieve victory!

## Features

* Randomly generated dungeon layouts
* Multiple enemy types:

  * Goblins
  * Skeletons
  * Orcs
  * Trolls
* Character progression system

  * Gain XP from defeating enemies
  * Level up and increase your stats
* Treasure chests containing:

  * Gold
  * Health restoration
* Increasing difficulty on deeper floors
* Health and XP system
* Victory and game over screens

## Controls

| Key   | Action               |
| ----- | -------------------- |
| W / ↑ | Move Up              |
| S / ↓ | Move Down            |
| A / ← | Move Left            |
| D / → | Move Right           |
| Enter | Start Game / Restart |

## How to Play

1. Start the game.
2. Explore the dungeon.
3. Walk into enemies to attack them.
4. Open treasure chests by walking onto them.
5. Find the stairs and descend to the next floor.
6. Defeat monsters to gain XP and gold.
7. Level up to become stronger.
8. Reach Floor 10 to win.

## Enemy Types

### Goblin

* Weakest enemy
* Low health
* Low damage

### Skeleton

* Balanced enemy
* Moderate health and damage

### Orc

* Strong enemy
* High health and damage

### Troll

* Most dangerous enemy
* Very high health
* Very high damage

## Progression

Every level-up grants:

* +2 Attack
* +8 Maximum HP
* HP restoration

Additionally, every 3 dungeon floors:

* +5 Maximum HP bonus

## Installation

### Requirements

* Python 3.11+
* Pygame Zero

### Install Pygame Zero

```bash
pip install pgzero
```

### Run the Game

```bash
pgzrun game2.py
```

## Project Structure

```text
game2.py
README.md
```

## Future Ideas

* Boss battles
* Weapons and armor
* Inventory system
* Magic spells
* Sound effects and music
* Save/load system
* Multiple dungeon themes

## Credits

Created with Python and Pygame Zero.

Have fun exploring the dungeon!
