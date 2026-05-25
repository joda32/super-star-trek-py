# Super Star Trek — Python Edition

```
           ,----------.  U.S.S. ENTERPRISE  NCC-1701
          /  NCC-1701   \
         |               |
   ,_____|_______________|________________________________,
  /                                                        \
 |                                                          |====>
  \_____|_______________|________________________________/
         |               |
          \_____________/
                 |
          ,______|______.
         /        |       \
        (         |        )=======>
         \________|_______/
```

> *"Space: the final frontier..."*

A faithful (with some creative curses additions) Python translation of the classic 1978 BASIC text adventure, rebuilt with a full-colour three-panel terminal UI using `curses`.  
**Python translation by [@joda32](https://github.com/joda32)**

---

## Origins & Credits

This was the first computer game I ever played on an old ICL cp/m machine. This is nothing but a thank you to the people who built the original.

Super Star Trek has a remarkable lineage stretching back over fifty years:

| Year | Author | Platform | Contribution |
|------|--------|----------|--------------|
| 1971 | **Mike Mayfield** | SDS Sigma 7 mainframe | Original *Star Trek* text game |
| 1973 | **David Ahl** | Various BASIC interpreters | Published in *101 BASIC Computer Games* |
| 1974 | **Bob Leedom** | Data General Nova 800 | Rewrote as *Super Star Trek* — added named commands, dynamic Klingon AI, crew dialogue |
| 1978 | **David Ahl** | All home micros | Published in *BASIC Computer Games — Microcomputer Edition*, the first computer book to sell one million copies |
| 2021+ | **coding-horror / basic-computer-games** | GitHub | Open-source preservation and multi-language revival |

---

## Requirements

- Python 3.8 or later
- `windows-curses` (Windows only — already native on macOS/Linux)

```bash
pip install windows-curses
```

## Running the Game

```bash
python startrek.py
```

Minimum terminal size: **72 × 22** characters. A standard 80 × 24 terminal works perfectly. Larger terminals give the message panel more room to scroll.

---

## Screenshots

### Splash Screen

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│           * * *   S U P E R   S T A R   T R E K   * * *                 │
│       A  Python  Translation  of  the  Classic  1978  BASIC  Game        │
│       ────────────────────────────────────────────────────               │
│            ,----------.  U.S.S. ENTERPRISE  NCC-1701                     │
│           /  NCC-1701   \                                                 │
│          |               |                                                │
│    ,_____|_______________|________________________________,               │
│   /                                                        \              │
│  |                                                          |====>        │
│   \_____|_______________|________________________________/               │
│          |               |                                                │
│           \_____________/                                                 │
│                  |                                                        │
│           ,______|______.                                                 │
│          /        |       \                                               │
│         (         |        )=======>                                      │
│          \________|_______/                                               │
│                   Python translation by:  @joda32                        │
│   ─ ─ ─   With  Thanks  To  The  Original  Creators   ─ ─ ─             │
│   Mike Mayfield   Star Trek (1971)  —  SDS Sigma 7 mainframe             │
│   Bob Leedom      Super Star Trek (1974)  —  Data General Nova 800       │
│   David Ahl       Creative Computing edition (1978)                       │
│              [ PRESS ANY KEY TO ENGAGE WARP DRIVE ]                      │
└──────────────────────────────────────────────────────────────────────────┘
```

### Main Game Screen

The interface is split into three bordered panels that update live after every command.

```
┌──── SUPER STAR TREK ────┐┌────────────── MESSAGES ──────────────────────┐
│ STARDATE:  2350         ││                                               │
│ CONDITION: GREEN        ││  YOUR ORDERS ARE AS FOLLOWS:                 │
│ QUADRANT:  4,3          ││    DESTROY THE KLINGON BATTLE GROUP          │
│ SECTOR:    2,6          ││    BEFORE THEY ATTACK FEDERATION HQ!         │
│ ENERGY:    3000         ││                                               │
│ TORPEDOES: 10           ││  MISSION BEGINS IN 'CANOPUS III'.            │
│ SHIELDS:   0            ││  17 KLINGON BATTLE CRUISERS DETECTED.        │
│ KLINGONS:  17           ││  FEDERATION NEEDS HELP IN 27 STARDATES.      │
├─────────────────────────┤│  3 STARBASES AVAILABLE.                      │
│  <*>             *      ││                                               │
│        *          *     ││                                               │
│                 *       ││                                               │
│   *      *              ││                                               │
│               *         ││                                               │
│  *    *                 ││                                               │
│           *      *      ││                                               │
│     *                   ││                                               │
│              *    *     ││                                               │
└─────────────────────────┘└───────────────────────────────────────────────┘
┌────────────────────────── COMMAND ────────────────────────────────────────┐
│ ENTER COMMAND: _                                                           │
│ NAV  SRS  LRS  PHA  TOR  SHE  DAM  COM  XXX                              │
└───────────────────────────────────────────────────────────────────────────┘
```

### Combat — Red Alert

When Klingons are in the quadrant the condition indicator turns `*RED*`. Every offensive action causes the Klingons to fire back immediately.

```
┌──── SUPER STAR TREK ────┐┌────────────── MESSAGES ──────────────────────┐
│ STARDATE:  2353         ││  ▶ PHA                                        │
│ CONDITION: *RED*        ││  ENERGY AVAIL=2850. UNITS TO FIRE:            │
│ QUADRANT:  4,3          ││  ▶ 500                                        │
│ SECTOR:    2,6          ││  375 UNITS HIT KLINGON AT 5,3                 │
│ ENERGY:    2350         ││  (KLINGON AT 5,3 HAS 112 UNITS REMAINING)     │
│ TORPEDOES: 10           ││  248 UNITS HIT KLINGON AT 7,6                 │
│ SHIELDS:   500          ││  *** KLINGON DESTROYED ***                    │
│ KLINGONS:  15           ││  KLINGON 5,3: SHIELDS HIT -89 → 411 LEFT      │
├─────────────────────────┤│                                               │
│  <*>        +K+    *   ││                                               │
│        *          *     ││                                               │
│   *                     ││                                               │
│         *    *          ││                                               │
│   *    *       *        ││                                               │
│                  *      ││                                               │
│     *      *            ││                                               │
│              *    *     ││                                               │
│   *                     ││                                               │
└─────────────────────────┘└───────────────────────────────────────────────┘
┌────────────────────────── COMMAND ────────────────────────────────────────┐
│ ENTER COMMAND: _                                                           │
│ NAV  SRS  LRS  PHA  TOR  SHE  DAM  COM  XXX                              │
└───────────────────────────────────────────────────────────────────────────┘
```

### Docked at Starbase

Navigate adjacent to a `>!<` starbase symbol to dock automatically. All systems are repaired and restocked at no cost.

```
┌──── SUPER STAR TREK ────┐┌────────────── MESSAGES ──────────────────────┐
│ STARDATE:  2361         ││  ▶ NAV                                        │
│ CONDITION: DOCKED       ││  COURSE (1-9): 3                              │
│ QUADRANT:  6,2          ││  WARP FACTOR (0-8): 0.5                       │
│ SECTOR:    4,4          ││  REPAIR: Phaser Control OPERATIONAL.          │
│ ENERGY:    3000         ││  SHIELDS DROPPED FOR DOCKING.                 │
│ TORPEDOES: 10           ││  STARBASE: ALL SYSTEMS REPAIRED AND           │
│ SHIELDS:   0            ││            RESTOCKED.                         │
│ KLINGONS:  11           ││                                               │
├─────────────────────────┤│                                               │
│   *    >!<  <*>   *    ││                                               │
│        *          *     ││                                               │
│                 *       ││                                               │
└─────────────────────────┘└───────────────────────────────────────────────┘
┌────────────────────────── COMMAND ────────────────────────────────────────┐
│ ENTER COMMAND: _                                                           │
│ NAV  SRS  LRS  PHA  TOR  SHE  DAM  COM  XXX                              │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Game Objective

You are Captain of the **U.S.S. Enterprise NCC-1701**. A Klingon battle fleet has invaded the galaxy, and Starfleet Command needs you to destroy every last one of them before they overwhelm Federation defences.

**You win** by destroying all Klingon battle cruisers before your stardates run out.  
**You lose** if:
- The Enterprise runs out of energy (destroyed in battle)
- The mission stardate expires with Klingons still alive
- All starbases are destroyed and you no longer have the energy to continue

### The Galaxy

The galaxy is an **8 × 8 grid of quadrants**. Each quadrant contains an **8 × 8 grid of sectors**. You begin in a random quadrant and must hunt down every Klingon hidden across all 64 quadrants.

### Map Symbols

| Symbol | Meaning |
|--------|---------|
| `<*>` | U.S.S. Enterprise (your ship) |
| `+K+` | Klingon battle cruiser |
| `>!<` | Federation Starbase |
| ` * ` | Star (blocks torpedoes) |

### Condition Indicator

| Condition | Meaning |
|-----------|---------|
| `GREEN` | All clear — no threats in current quadrant |
| `YELLOW` | Warning — energy is critically low |
| `*RED*` | Combat alert — Klingons are in this quadrant |
| `DOCKED` | Secured at a starbase — safe and being replenished |

### Resources

| Resource | Starting Amount | Notes |
|----------|----------------|-------|
| Energy | 3,000 units | Shared with shields; replenished at starbases |
| Photon Torpedoes | 10 | Guaranteed one-hit kill; restocked at starbases |
| Stardates | 25–35 | One consumed per warp jump; clock never stops |

---

## Command Reference

Type any command at the `ENTER COMMAND:` prompt and press **Enter**.

---

### `NAV` — Warp Navigation

Moves the Enterprise through space.

```
COURSE (1-9): 3
WARP FACTOR (0-8): 2
```

**Course dial** — 8 compass directions plus wrap-around:

```
       NW  N  NE
        4  3  2
  W  5  .  .  .  1  E
        6  7  8
       SW  S  SE
```

Decimal courses are allowed (`3.5` flies north-west, for example).

**Warp factor** controls speed and energy cost. Each warp unit traverses 8 sectors and costs 8 energy units.  
Moving into a new quadrant takes one stardate. Damaged warp engines are limited to **Warp 0.2**.

> **Tip:** Entering warp `0` cancels the command without consuming energy.

---

### `SRS` — Short Range Sensor Scan

Refreshes the left panel to show all objects in your current 8 × 8 sector quadrant.  
No energy cost. Useless if **Short Range Sensors** are damaged.

---

### `LRS` — Long Range Sensor Scan

Reveals the 3 × 3 block of quadrants surrounding your current position, showing a three-digit summary for each: `KBS` where **K** = Klingons, **B** = Starbases, **S** = Stars.

```
     +-----+-----+-----+
     |  000 |  102 |  010 |
     +-----+-----+-----+
     |  100 | >4,3<|  001 |
     +-----+-----+-----+
     |  000 |  200 |  000 |
     +-----+-----+-----+
```

Scanned quadrants are added to your galactic record (`COM` option 0).  
No energy cost. Useless if **Long Range Sensors** are damaged.

---

### `PHA` — Phaser Control

Fires phasers at all Klingons in the current quadrant simultaneously.

```
ENERGY AVAIL=2850. UNITS TO FIRE: 400
```

- You choose how many energy units to expend.
- Damage dealt **falls off with distance** — a Klingon on the far side of the quadrant receives less damage than one nearby.
- All Klingons in the quadrant are hit; energy is divided equally among them.
- Klingons **fire back** immediately after your shot.
- A damaged **Library Computer** reduces accuracy by up to 50%.

> **Tip:** Check `COM` option 2 for torpedo data to see each Klingon's distance before deciding how many units to fire.

---

### `TOR` — Photon Torpedo

Fires a single photon torpedo on a set course.

```
TORPEDO COURSE (1-9): 2
```

Uses the same **course dial** as `NAV`. The torpedo travels in a straight line until it hits something or exits the quadrant.

- **One torpedo = one guaranteed Klingon kill** (if it hits).
- Torpedoes can also destroy **Starbases** (triggers a Starfleet court-martial review — avoid this).
- **Stars absorb** torpedo hits — they can shield Klingons hiding behind them.
- Klingons **fire back** after a torpedo is launched.
- Each torpedo costs 1 torpedo + 2 energy.

> **Tip:** Use `COM` option 2 for exact torpedo course and distance data before firing.

---

### `SHE` — Shield Control

Transfers energy between the ship's main power and the defensive shields.

```
TOTAL ENERGY AVAILABLE = 3000
UNITS TO SHIELDS: 500
```

- Shields absorb incoming Klingon fire proportionally.
- Raising or lowering shields **does not** cost extra energy — you are simply moving energy between two pools.
- Shields are **automatically dropped** when docking at a starbase.
- If **Shield Control** is damaged the command is unavailable.

> **Tip:** Keep at least 300–500 units in shields whenever Klingons are present. Letting shields reach zero exposes your hull directly to weapons fire.

---

### `DAM` — Damage Control Report

Displays the repair status of all eight ship systems.

```
DEVICE                   STATE
---------------------------------
Warp Engines             OPERATIONAL
Short Range Sensors      OPERATIONAL
Long Range Sensors       DAMAGED (-2.31)
Phaser Control           OPERATIONAL
Photon Torpedo Tubes     OPERATIONAL
Shield Control           DAMAGED (-0.74)
Library Computer         OPERATIONAL
Damage Control           OPERATIONAL
```

Negative values show how many warp-units of travel remain before automatic repair is complete. Docking at a **Starbase** repairs all systems instantly.

---

### `COM` — Library Computer

Accesses six sub-functions of the ship's computer. Requires an **operational Library Computer**.

```
LIBRARY COMPUTER OPTIONS:
  0  GALACTIC RECORD
  1  STATUS REPORT
  2  PHOTON TORPEDO DATA
  3  STARBASE NAV DATA
  4  DIRECTION/DISTANCE CALC
  5  GALAXY MAP
OPTION: _
```

| Option | Function |
|--------|----------|
| `0` | Galactic record — table of all quadrants scanned by long-range sensors |
| `1` | Full status report — stardate, condition, resources and time remaining |
| `2` | Torpedo targeting data — exact course and distance to each Klingon in the quadrant |
| `3` | Starbase navigation — course and distance to the nearest starbase in the quadrant |
| `4` | Direction/distance calculator — enter any two sector coordinates for a course reading |
| `5` | Galaxy map — 8 × 8 overview of explored space with your current position marked |

---

### `XXX` — Abandon Mission

Ends the game immediately.

---

## Strategy & Tips

### Early Game

1. **Run `LRS` in your starting quadrant** before doing anything else. This reveals the surrounding 8 quadrants for free and fills in your galactic record — intelligence you will use all game.
2. **Allocate shields early.** Use `SHE` to move 300–500 units into shields before entering any quadrant that might have Klingons.
3. **Locate the nearest starbase.** Starbases are your lifeline. Know where the closest one is before you need it.

### Navigation

- **Warp 1–2** for short hops within a region — cheap and precise.
- **Warp 5–8** for cross-galaxy pursuits — burns energy fast but saves stardates.
- The Enterprise stops automatically if its path is blocked by a star or object. Check `SRS` after every warp to orientate yourself.
- **Impulse travel** (warp < 1) moves only within the current quadrant and costs very little energy.

### Combat

- **Use `COM` option 2 before firing** to get the exact torpedo course. A missed torpedo wastes a scarce resource.
- **Phasers scale with distance.** Get close before firing — a nearby Klingon receives far more damage per energy unit than a distant one.
- **Torpedoes are one-hit kills** regardless of distance. Prefer them when you can aim accurately.
- **After destroying all Klingons in a quadrant** the condition drops to GREEN — you are safe to manoeuvre freely.

### Resource Management

- **Never let energy drop below ~500** without a plan to reach a starbase.
- Shields must be lowered to zero to dock — fly adjacent to a `>!<` with shields already at 0 to avoid wasting energy.
- Each warp jump costs energy *and* a stardate. High warp burns both faster. Balance speed against reserves.
- **Damaged systems persist** until you reach a starbase or accumulate enough warp travel for auto-repair. Prioritise reaching a base if your phasers, torpedoes, or shields are out.

### Endgame

- The galaxy map (`COM` option 5) marks every quadrant you have scanned. Any quadrant still showing `**` is unexplored — Klingons could be hiding there.
- Track remaining Klingons on the status report (`COM` option 1). Cross-reference with the galactic record to identify which quadrants still contain enemy ships.
- **Watch the stardate clock.** If you are low on time, set maximum warp and head directly for the densest Klingon concentrations.

---

## Ship Systems Reference

| System | Damaged Effect |
|--------|---------------|
| Warp Engines | Maximum warp capped at 0.2 |
| Short Range Sensors | `SRS` command disabled |
| Long Range Sensors | `LRS` command disabled |
| Phaser Control | `PHA` command disabled |
| Photon Torpedo Tubes | `TOR` command disabled |
| Shield Control | `SHE` command disabled |
| Library Computer | `COM` command disabled; phaser accuracy halved |
| Damage Control | Repair rate unaffected (the ship always heals itself) |

Systems repair automatically during warp travel. The faster the warp, the faster the repair. Docking at a **Starbase** repairs everything instantly.

---

## Acknowledgements

This Python edition stands on the shoulders of the original creators:

- **Mike Mayfield** — *Star Trek* (1971), SDS Sigma 7 mainframe. The game that started it all.
- **Bob Leedom** — *Super Star Trek* (1974), Data General Nova 800. Added named commands (`NAV`, `PHA`, `TOR`…), dynamic Klingon AI that moves and retaliates, crew character dialogue, and named quadrants.
- **David Ahl / Creative Computing** — Published the definitive edition in *BASIC Computer Games — Microcomputer Edition* (1978). The first computer book to sell one million copies.
- **coding-horror / [basic-computer-games](https://github.com/coding-horror/basic-computer-games)** — Open-source preservation project keeping classic BASIC games alive across modern languages.

Python translation by **[@joda32](https://github.com/joda32)**.

---

*"To boldly go where no BASIC interpreter has gone before."*
