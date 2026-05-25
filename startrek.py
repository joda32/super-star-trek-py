"""
SUPER STAR TREK
Translated from the 1978 BASIC version by Bob Leedom / David Ahl
Original: Creative Computing, Morristown NJ

Requires: windows-curses  (pip install windows-curses)
"""

import random
import math
import sys

try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QUADRANT_SIZE = 8
GALAXY_SIZE = 8

DEVICE_NAMES = [
    "Warp Engines",
    "Short Range Sensors",
    "Long Range Sensors",
    "Phaser Control",
    "Photon Torpedo Tubes",
    "Shield Control",
    "Library Computer",
    "Damage Control",
]

QUADRANT_NAMES = [
    ["ANTARES",  "RIGEL",       "PROCYON",     "VEGA",      "CANOPUS",  "ALTAIR",   "SAGITTARIUS", "POLLUX"],
    ["SIRIUS",   "DENEB",       "CYGNUS",      "CAPELLA",   "BETELGEUSE","ALDEBARAN","REGULUS",     "ARCTURUS"],
    ["SPICA",    "GAMMA HYDRA", "ELECTRA",     "ACRUX",     "MIZAR",    "ASCELLA",  "ARRAKIS",     "RIGEL"],
    ["SHAULA",   "ZUBEN",       "GROOMBRIDGE", "RASALHAGUE","ALPHECCA", "ALBIREO",  "ANTARES",     "FOMALHAUT"],
]
QUADRANT_NUMBER_SUFFIX = ["I", "II", "III", "IV"]

# Course 1-9: direction unit vectors (row_delta, col_delta)
# Course 1 = East, 3 = North, 5 = West, 7 = South
DIRECTION_VECTORS = [
    ( 0,  0),   # 0 — unused
    ( 0,  1),   # 1
    (-1,  1),   # 2
    (-1,  0),   # 3
    (-1, -1),   # 4
    ( 0, -1),   # 5
    ( 1, -1),   # 6
    ( 1,  0),   # 7
    ( 1,  1),   # 8
    ( 0,  1),   # 9 == 1
]

# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------

class Enterprise:
    def __init__(self):
        self.energy    = 3000
        self.shields   = 0
        self.torpedoes = 10
        self.quadrant  = [random.randint(0, 7), random.randint(0, 7)]
        self.sector    = [random.randint(0, 7), random.randint(0, 7)]
        self.damage    = [0.0] * 8
        self.docked    = False


class GameState:
    def __init__(self):
        self.stardate        = random.randint(20, 39) * 100
        self.mission_end     = self.stardate + 25 + random.randint(0, 9)
        self.enterprise      = Enterprise()
        self.galaxy          = [[0] * GALAXY_SIZE for _ in range(GALAXY_SIZE)]
        self.charted         = [[False] * GALAXY_SIZE for _ in range(GALAXY_SIZE)]
        self.klingons_remaining  = 0
        self.starbases_remaining = 0
        self.klingon_positions   = []   # [row, col, energy]
        self.quadrant_map        = []
        self._init_galaxy()
        self._enter_quadrant()

    # ------------------------------------------------------------------
    def _init_galaxy(self):
        total_k = 0
        total_b = 0
        for r in range(GALAXY_SIZE):
            for c in range(GALAXY_SIZE):
                rng = random.random()
                k = 3 if rng > 0.98 else (2 if rng > 0.95 else (1 if rng > 0.80 else 0))
                b = 1 if random.random() > 0.96 else 0
                s = random.randint(1, 8)
                self.galaxy[r][c] = k * 100 + b * 10 + s
                total_k += k
                total_b += b
        if total_k < 15:
            r, c = random.randint(0, 7), random.randint(0, 7)
            extra = 15 - total_k
            k = min(9, (self.galaxy[r][c] // 100) + extra)
            self.galaxy[r][c] = (self.galaxy[r][c] % 100) + k * 100
            total_k = 15
        if total_b < 2:
            r, c = random.randint(0, 7), random.randint(0, 7)
            b = (self.galaxy[r][c] // 10 % 10) + 1
            self.galaxy[r][c] = (self.galaxy[r][c] // 100) * 100 + b * 10 + (self.galaxy[r][c] % 10)
        self.klingons_remaining  = total_k
        self.starbases_remaining = total_b

    def _enter_quadrant(self):
        e   = self.enterprise
        qr, qc = e.quadrant
        cell    = self.galaxy[qr][qc]
        k_count = cell // 100
        b_count = (cell // 10) % 10
        s_count = cell % 10
        self.charted[qr][qc] = True

        grid = [["   "] * QUADRANT_SIZE for _ in range(QUADRANT_SIZE)]
        sr, sc = e.sector
        grid[sr][sc] = "<*>"

        self.klingon_positions = []
        placed = self._place_objects(grid, "+K+", k_count, exclude=[(sr, sc)])
        for pr, pc in placed:
            self.klingon_positions.append([pr, pc, 100 + random.randint(0, 199)])
        self._place_objects(grid, ">!<", b_count, exclude=[(sr, sc)])
        self._place_objects(grid, " * ", s_count, exclude=[(sr, sc)])
        self.quadrant_map = grid

    def _place_objects(self, grid, symbol, count, exclude):
        placed = []
        for _ in range(200):
            if len(placed) >= count:
                break
            r, c = random.randint(0, 7), random.randint(0, 7)
            if grid[r][c] == "   " and (r, c) not in exclude:
                grid[r][c] = symbol
                placed.append((r, c))
        return placed

    def _find_in_grid(self, symbol):
        return [(r, c)
                for r in range(QUADRANT_SIZE)
                for c in range(QUADRANT_SIZE)
                if self.quadrant_map[r][c] == symbol]

    def quadrant_name(self, qr=None, qc=None):
        if qr is None:
            qr, qc = self.enterprise.quadrant
        nr = min(qr // 2, len(QUADRANT_NAMES) - 1)
        nc = min(qc // 2, len(QUADRANT_NAMES[0]) - 1)
        si = (qr % 2) * 2 + (qc % 2)
        return f"{QUADRANT_NAMES[nr][nc]} {QUADRANT_NUMBER_SUFFIX[si]}"


# ---------------------------------------------------------------------------
# Terminal UI — three bordered panels
# ---------------------------------------------------------------------------

class GameUI:
    """
    Layout (example 100×28 terminal):

    ┌───── SUPER STAR TREK ─────┐┌──────── MESSAGES ────────────────┐
    │ STARDATE:  2345           ││                                    │
    │ CONDITION: *RED*          ││  YOUR MISSION BEGINS IN ...       │
    │ QUADRANT:  3,4            ││  THERE ARE 17 KLINGON CRUISERS.   │
    │ SECTOR:    5,2            ││                                    │
    │ ENERGY:    2850           ││  COMBAT ALERT! 2 KLINGONS HERE!   │
    │ TORPEDOES: 10             ││  KLINGON AT 4,3 FIRES: -150 SHLD  │
    │ SHIELDS:   500            ││  SHIELDS NOW AT 350 UNITS.        │
    │ KLINGONS:  14             ││                                    │
    ├───────────────────────────┤│                                    │
    │  <*>   *      +K+        ││                                    │
    │   *         *             ││                                    │
    │        +K+       *       ││                                    │
    │  *              *         ││                                    │
    │       >!<                 ││                                    │
    │  *         *     *        ││                                    │
    │                    *      ││                                    │
    │        *                  ││                                    │
    │   *              *        ││                                    │
    └───────────────────────────┘└────────────────────────────────────┘
    ┌──────────────────────────────── COMMAND ─────────────────────────┐
    │ ENTER COMMAND: _                                                   │
    │ NAV  SRS  LRS  PHA  TOR  SHE  DAM  COM  XXX                      │
    └───────────────────────────────────────────────────────────────────┘
    """

    MAP_W   = 30   # left panel total width (auto-expands on wide terms)
    CMD_H   = 4    # command panel total height
    MIN_W   = 72
    MIN_H   = 22

    def __init__(self, stdscr):
        self.stdscr   = stdscr
        self.messages = []
        self._gs      = None

        curses.curs_set(0)
        if curses.has_colors():
            curses.start_color()
            try:
                curses.use_default_colors()
                bg = -1
            except Exception:
                bg = curses.COLOR_BLACK
            curses.init_pair(1, curses.COLOR_GREEN,  bg)  # normal / enterprise
            curses.init_pair(2, curses.COLOR_RED,    bg)  # klingon / red alert
            curses.init_pair(3, curses.COLOR_YELLOW, bg)  # starbase / yellow alert
            curses.init_pair(4, curses.COLOR_CYAN,   bg)  # borders / labels
            curses.init_pair(5, curses.COLOR_WHITE,  bg)  # stars / dimmed text
        self._has_color = curses.has_colors()

        self._setup_windows()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_windows(self):
        H, W = self.stdscr.getmaxyx()
        if H < self.MIN_H or W < self.MIN_W:
            raise RuntimeError(
                f"Terminal too small ({W}x{H}). Need at least {self.MIN_W}x{self.MIN_H}."
            )
        self.H = H
        self.W = W

        # Left panel: slightly less than half, minimum 28
        map_w = max(28, min(W // 2, 36))
        out_w = W - map_w
        top_h = H - self.CMD_H
        cmd_h = self.CMD_H

        self.map_win = curses.newwin(top_h, map_w, 0, 0)
        self.out_win = curses.newwin(top_h, out_w, 0, map_w)
        self.cmd_win = curses.newwin(cmd_h, W, top_h, 0)

        self._map_w  = map_w
        self._out_w  = out_w
        self._top_h  = top_h

        self._map_iw = map_w - 2   # inner width
        self._map_ih = top_h - 2   # inner height
        self._out_iw = out_w - 2
        self._out_ih = top_h - 2
        self._cmd_iw = W - 2

    # ------------------------------------------------------------------
    # Color helpers
    # ------------------------------------------------------------------

    def _cp(self, n, bold=False):
        attr = curses.color_pair(n) if self._has_color else curses.A_NORMAL
        if bold:
            attr |= curses.A_BOLD
        return attr

    # ------------------------------------------------------------------
    # Public API used by game logic
    # ------------------------------------------------------------------

    def set_game_state(self, gs):
        self._gs = gs

    def gprint(self, text=""):
        """Append text to the scrolling message log, wrapping long lines."""
        iw = self._out_iw
        for raw_line in str(text).split("\n"):
            if not raw_line:
                self.messages.append("")
                continue
            while raw_line:
                self.messages.append(raw_line[:iw])
                raw_line = raw_line[iw:]
        self._refresh_output()

    def ginput(self, prompt=""):
        """Show prompt in command panel, read a line of input, return it."""
        display = prompt if prompt else "ENTER COMMAND: "
        self._draw_cmd_window(display)
        result = self._read_line(display)
        return result

    def refresh_map(self):
        if self._gs:
            self._draw_map_panel(self._gs)

    def wait_key(self, msg="PRESS ANY KEY TO CONTINUE..."):
        self.gprint(msg)
        self.cmd_win.nodelay(False)
        self.cmd_win.getch()

    # ------------------------------------------------------------------
    # Map / status panel
    # ------------------------------------------------------------------

    def _draw_map_panel(self, gs):
        win  = self.map_win
        mw   = self._map_w
        iw   = self._map_iw
        win.erase()

        # Border + title
        win.attron(self._cp(4))
        win.box()
        title = " SUPER STAR TREK "
        try:
            win.addstr(0, max(1, (mw - len(title)) // 2), title,
                       self._cp(4, bold=True))
        except curses.error:
            pass
        win.attroff(self._cp(4))

        e    = gs.enterprise
        cond = condition_str(gs)
        cond_attr = (
            self._cp(2, bold=True) if cond == "*RED*" else
            self._cp(3, bold=True) if cond == "YELLOW" else
            self._cp(1)
        )

        def stat2(row, lbl1, val1, lbl2, val2, v_attr=None):
            v_attr = v_attr or self._cp(1, bold=True)
            c2 = iw // 2 + 1
            try:
                win.addstr(row, 2, lbl1, self._cp(4))
                win.addstr(row, 2 + len(lbl1), str(val1)[:c2 - len(lbl1) - 1], v_attr)
                win.addstr(row, c2 + 1, lbl2, self._cp(4))
                win.addstr(row, c2 + 1 + len(lbl2), str(val2)[:iw - c2 - len(lbl2)], v_attr)
            except curses.error:
                pass

        def stat1(row, lbl, val, v_attr=None):
            v_attr = v_attr or self._cp(1, bold=True)
            try:
                win.addstr(row, 2, lbl, self._cp(4))
                win.addstr(row, 2 + len(lbl), str(val)[:iw - len(lbl) - 1], v_attr)
            except curses.error:
                pass

        stat1(1, "STARDATE:  ", gs.stardate)
        stat1(2, "CONDITION: ", cond, cond_attr)
        stat2(3, "QUADRANT: ", f"{e.quadrant[0]+1},{e.quadrant[1]+1}",
              "SECTOR: ", f"{e.sector[0]+1},{e.sector[1]+1}")
        stat2(4, "ENERGY:   ", e.energy, "SHIELDS: ", e.shields)
        stat2(5, "TORPEDOES:", e.torpedoes, "KLNGNS:  ", gs.klingons_remaining)

        # Horizontal divider after stats
        div_row = 6
        try:
            win.addch(div_row, 0,      curses.ACS_LTEE,  self._cp(4))
            win.attron(self._cp(4))
            win.hline(div_row, 1, curses.ACS_HLINE, iw)
            win.attroff(self._cp(4))
            win.addch(div_row, mw - 1, curses.ACS_RTEE,  self._cp(4))
        except curses.error:
            pass

        # Quadrant grid — entity colour map
        E_ATTR = {
            "<*>": self._cp(1, bold=True),
            "+K+": self._cp(2, bold=True),
            ">!<": self._cp(3, bold=True),
            " * ": self._cp(5),
            "   ": self._cp(5),
        }

        grid_start_row = div_row + 1
        for r in range(QUADRANT_SIZE):
            grow = grid_start_row + r
            if grow > self._map_ih:
                break
            col = 2
            for c in range(QUADRANT_SIZE):
                cell = gs.quadrant_map[r][c]
                attr = E_ATTR.get(cell, self._cp(1))
                try:
                    win.addstr(grow, col, cell, attr)
                except curses.error:
                    pass
                col += 4   # 3 chars + 1 space

        win.noutrefresh()
        curses.doupdate()

    # ------------------------------------------------------------------
    # Output / message panel
    # ------------------------------------------------------------------

    def _refresh_output(self):
        win = self.out_win
        ow  = self._out_w
        ih  = self._out_ih
        iw  = self._out_iw

        win.erase()
        win.attron(self._cp(4))
        win.box()
        title = " MESSAGES "
        try:
            win.addstr(0, max(1, (ow - len(title)) // 2), title,
                       self._cp(4, bold=True))
        except curses.error:
            pass
        win.attroff(self._cp(4))

        visible = self.messages[-ih:]
        for i, msg in enumerate(visible):
            if i >= ih:
                break
            try:
                win.addstr(i + 1, 1, msg[:iw], self._cp(5))
            except curses.error:
                pass

        win.noutrefresh()
        curses.doupdate()

    # ------------------------------------------------------------------
    # Command panel
    # ------------------------------------------------------------------

    def _draw_cmd_window(self, prompt="ENTER COMMAND: "):
        win = self.cmd_win
        W   = self.W

        win.erase()
        win.attron(self._cp(4))
        win.box()
        title = " COMMAND "
        try:
            win.addstr(0, max(1, (W - len(title)) // 2), title,
                       self._cp(4, bold=True))
        except curses.error:
            pass
        win.attroff(self._cp(4))

        hint = "NAV  SRS  LRS  PHA  TOR  SHE  DAM  COM  XXX"
        try:
            win.addstr(1, 2, prompt, self._cp(3, bold=True))
            win.addstr(2, 2, hint,   self._cp(4))
        except curses.error:
            pass

        win.noutrefresh()
        curses.doupdate()

    # ------------------------------------------------------------------
    # Input reader
    # ------------------------------------------------------------------

    def _read_line(self, prompt):
        win       = self.cmd_win
        prompt_col = 2 + len(prompt)
        max_chars  = max(1, self._cmd_iw - prompt_col - 1)

        curses.curs_set(1)
        curses.echo()
        try:
            win.move(1, prompt_col)
            win.refresh()
            raw    = win.getstr(1, prompt_col, max_chars)
            result = raw.decode("utf-8", errors="replace").strip()
        except (curses.error, Exception):
            result = ""
        finally:
            curses.noecho()
            curses.curs_set(0)

        # Echo the command into the message log
        self.messages.append(f"▶ {result}")
        self._refresh_output()
        self._draw_cmd_window()
        return result


# ---------------------------------------------------------------------------
# Game helpers
# ---------------------------------------------------------------------------

def condition_str(gs):
    e = gs.enterprise
    if e.docked:
        return "DOCKED"
    k = gs.galaxy[e.quadrant[0]][e.quadrant[1]] // 100
    if k > 0:
        return "*RED*"
    if e.energy < 300 + e.shields:
        return "YELLOW"
    return "GREEN"


def _calc_direction(from_r, from_c, to_r, to_c):
    dr   = to_r - from_r
    dc   = to_c - from_c
    dist = math.sqrt(dr ** 2 + dc ** 2)
    if dist == 0:
        return 1.0, 0.0
    angle  = math.atan2(dc, -dr)
    if angle < 0:
        angle += 2 * math.pi
    course = (angle / (2 * math.pi)) * 8 + 1
    return round(course, 2), round(dist, 2)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_srs(gs, ui):
    ui.gprint("[ SHORT RANGE SENSORS — map refreshed ]")
    ui.refresh_map()


def cmd_lrs(gs, ui):
    e = gs.enterprise
    if e.damage[2] < 0:
        ui.gprint("LONG RANGE SENSORS DAMAGED.")
        return
    qr, qc = e.quadrant
    ui.gprint(f"LONG RANGE SCAN FOR QUADRANT {qr+1},{qc+1}")
    sep = "     +" + "-----+" * 3
    ui.gprint(sep)
    for dr in range(-1, 2):
        parts = []
        for dc in range(-1, 2):
            r2, c2 = qr + dr, qc + dc
            if 0 <= r2 < GALAXY_SIZE and 0 <= c2 < GALAXY_SIZE:
                gs.charted[r2][c2] = True
                parts.append(f" {gs.galaxy[r2][c2]:03d} ")
            else:
                parts.append(" *** ")
        ui.gprint("     |" + "|".join(parts) + "|")
        ui.gprint(sep)


def cmd_nav(gs, ui):
    e = gs.enterprise
    if e.damage[0] < 0:
        ui.gprint("WARP ENGINES DAMAGED. MAX WARP = 0.2")
    try:
        course = float(ui.ginput("COURSE (1-9): "))
        if not 1.0 <= course <= 9.0:
            ui.gprint("SULU: 'INCORRECT COURSE DATA, SIR!'")
            return
    except ValueError:
        ui.gprint("INVALID INPUT.")
        return

    max_warp = 0.2 if e.damage[0] < 0 else 8.0
    try:
        warp = float(ui.ginput(f"WARP FACTOR (0-{max_warp}): "))
        if warp < 0 or warp > max_warp:
            ui.gprint("WARP FACTOR OUT OF RANGE.")
            return
        if warp == 0:
            return
    except ValueError:
        ui.gprint("INVALID INPUT.")
        return

    energy_needed = int(warp * 8 + 0.5)
    if energy_needed > e.energy - e.shields:
        ui.gprint("ENGINEERING: 'INSUFFICIENT ENERGY FOR MANEUVERING AT WARP!'")
        return

    # Incremental repairs during transit
    for i in range(8):
        if e.damage[i] < 0:
            e.damage[i] += warp
            if e.damage[i] >= 0:
                e.damage[i] = 0
                ui.gprint(f"REPAIR: {DEVICE_NAMES[i]} OPERATIONAL.")

    # Random new damage
    if random.random() <= 0.25:
        idx = random.randint(0, 7)
        e.damage[idx] -= random.random() * 5
        ui.gprint(f"DAMAGE: {DEVICE_NAMES[idx]} DAMAGED.")

    e.energy  -= energy_needed
    gs.stardate += 1

    # Compute movement delta per step
    idx  = int(course)
    frac = course - idx
    if idx == 9:
        idx = 1
    dr1, dc1 = DIRECTION_VECTORS[idx]
    dr2, dc2 = DIRECTION_VECTORS[idx + 1] if idx < 8 else DIRECTION_VECTORS[1]
    move_r = dr1 + (dr2 - dr1) * frac
    move_c = dc1 + (dc2 - dc1) * frac

    steps = int(warp * 8 + 0.5)
    sr, sc = float(e.sector[0]), float(e.sector[1])
    qr, qc = e.quadrant[0], e.quadrant[1]

    for _ in range(steps):
        new_sr = sr + move_r
        new_sc = sc + move_c
        new_qr, new_qc = qr, qc
        crossed = False

        if new_sr < 0:
            new_qr -= 1; new_sr = QUADRANT_SIZE - 1; crossed = True
        elif new_sr >= QUADRANT_SIZE:
            new_qr += 1; new_sr = 0;                  crossed = True
        if new_sc < 0:
            new_qc -= 1; new_sc = QUADRANT_SIZE - 1; crossed = True
        elif new_sc >= QUADRANT_SIZE:
            new_qc += 1; new_sc = 0;                  crossed = True

        if not (0 <= new_qr < GALAXY_SIZE and 0 <= new_qc < GALAXY_SIZE):
            ui.gprint("STARFLEET: 'TRAVEL OUTSIDE GALAXY DENIED'")
            break

        if crossed:
            gs.quadrant_map[int(sr)][int(sc)] = "   "
            sr, sc = new_sr, new_sc
            qr, qc = new_qr, new_qc
            e.sector   = [int(sr), int(sc)]
            e.quadrant = [qr, qc]
            e.docked   = False
            gs._enter_quadrant()
            cell = gs.galaxy[qr][qc]
            k3 = cell // 100
            b3 = (cell // 10) % 10
            if k3 > 0:
                ui.gprint(f"COMBAT ALERT! {k3} KLINGON{'S' if k3>1 else ''} IN QUADRANT {qr+1},{qc+1}!")
            if b3 > 0:
                ui.gprint(f"STARBASE IN QUADRANT {qr+1},{qc+1}.")
            gs.quadrant_map[int(sr)][int(sc)] = "<*>"
            break

        isr, isc = int(new_sr), int(new_sc)
        if gs.quadrant_map[isr][isc] != "   ":
            ui.gprint(f"WARP SHUT DOWN — OBSTACLE AT SECTOR {isr+1},{isc+1}.")
            break

        gs.quadrant_map[int(sr)][int(sc)] = "   "
        sr, sc = new_sr, new_sc
        gs.quadrant_map[int(sr)][int(sc)] = "<*>"

    e.sector   = [int(sr), int(sc)]
    e.quadrant = [qr, qc]
    _check_docking(gs, ui)
    ui.refresh_map()


def cmd_pha(gs, ui):
    e = gs.enterprise
    if e.damage[3] < 0:
        ui.gprint("PHASERS INOPERATIVE.")
        return
    if not gs.klingon_positions:
        ui.gprint("SPOCK: 'NO ENEMY SHIPS IN THIS QUADRANT.'")
        return
    if e.damage[6] < 0:
        ui.gprint("COMPUTER FAILURE HAMPERS ACCURACY.")
    try:
        avail  = e.energy - e.shields
        amount = int(ui.ginput(f"ENERGY AVAIL={avail}. UNITS TO FIRE: "))
    except ValueError:
        ui.gprint("INVALID.")
        return
    if amount <= 0:
        return
    if amount > e.energy - e.shields:
        ui.gprint("NOT ENOUGH ENERGY.")
        return

    e.energy -= amount
    destroyed = []
    for i, (kr, kc, ke) in enumerate(gs.klingon_positions):
        dist = math.sqrt((e.sector[0] - kr) ** 2 + (e.sector[1] - kc) ** 2) or 0.5
        hit  = int((amount / len(gs.klingon_positions)) * (random.random() + 2) / (dist + 0.5))
        if e.damage[6] < 0:
            hit = int(hit * (0.5 + random.random() * 0.5))
        ke -= hit
        ui.gprint(f"{hit} UNITS HIT KLINGON AT {kc+1},{kr+1}")
        if ke <= 0:
            ui.gprint("*** KLINGON DESTROYED ***")
            gs.quadrant_map[kr][kc] = "   "
            gs.galaxy[e.quadrant[0]][e.quadrant[1]] -= 100
            gs.klingons_remaining -= 1
            destroyed.append(i)
        else:
            ui.gprint(f"  ({ke} UNITS REMAINING)")
            gs.klingon_positions[i][2] = ke

    for i in reversed(destroyed):
        gs.klingon_positions.pop(i)

    _klingons_fire(gs, ui)
    ui.refresh_map()


def cmd_tor(gs, ui):
    e = gs.enterprise
    if e.damage[4] < 0:
        ui.gprint("PHOTON TORPEDO TUBES DAMAGED.")
        return
    if e.torpedoes <= 0:
        ui.gprint("ALL PHOTON TORPEDOES EXPENDED.")
        return
    if not gs.klingon_positions:
        ui.gprint("SPOCK: 'NO ENEMY SHIPS IN THIS QUADRANT.'")
        return
    try:
        course = float(ui.ginput("TORPEDO COURSE (1-9): "))
        if not 1.0 <= course <= 9.0:
            ui.gprint("CHEKOV: 'INCORRECT COURSE DATA, SIR!'")
            return
    except ValueError:
        ui.gprint("INVALID.")
        return

    e.torpedoes -= 1
    e.energy    -= 2

    idx  = int(course)
    frac = course - idx
    if idx == 9:
        idx = 1
    dr1, dc1 = DIRECTION_VECTORS[idx]
    dr2, dc2 = DIRECTION_VECTORS[idx + 1] if idx < 8 else DIRECTION_VECTORS[1]
    move_r = dr1 + (dr2 - dr1) * frac
    move_c = dc1 + (dc2 - dc1) * frac

    tr, tc = float(e.sector[0]), float(e.sector[1])
    ui.gprint("TORPEDO TRACK:")
    hit = False

    for _ in range(20):
        tr += move_r
        tc += move_c
        itr, itc = int(tr + 0.5), int(tc + 0.5)

        if not (0 <= itr < QUADRANT_SIZE and 0 <= itc < QUADRANT_SIZE):
            ui.gprint("   TORPEDO MISSED.")
            hit = True
            break

        ui.gprint(f"   {itr+1},{itc+1}")
        cell = gs.quadrant_map[itr][itc]

        if cell == "+K+":
            ui.gprint("*** KLINGON DESTROYED ***")
            gs.quadrant_map[itr][itc] = "   "
            gs.galaxy[e.quadrant[0]][e.quadrant[1]] -= 100
            gs.klingons_remaining -= 1
            for j, kp in enumerate(gs.klingon_positions):
                if kp[0] == itr and kp[1] == itc:
                    gs.klingon_positions.pop(j)
                    break
            hit = True
            break
        elif cell == ">!<":
            ui.gprint("*** STARBASE DESTROYED ***")
            ui.gprint("STARFLEET REVIEWING YOUR RECORD FOR COURT-MARTIAL!")
            gs.quadrant_map[itr][itc] = "   "
            gs.galaxy[e.quadrant[0]][e.quadrant[1]] -= 10
            gs.starbases_remaining -= 1
            e.docked = False
            hit = True
            break
        elif cell == " * ":
            ui.gprint(f"STAR AT {itc+1},{itr+1} ABSORBED TORPEDO.")
            hit = True
            break

    if not hit:
        ui.gprint("TORPEDO MISSED.")

    _klingons_fire(gs, ui)
    ui.refresh_map()


def cmd_she(gs, ui):
    e = gs.enterprise
    if e.damage[5] < 0:
        ui.gprint("SHIELD CONTROL DAMAGED.")
        return
    total = e.energy + e.shields
    ui.gprint(f"TOTAL ENERGY AVAILABLE = {total}")
    try:
        amount = int(ui.ginput("UNITS TO SHIELDS: "))
    except ValueError:
        ui.gprint("INVALID.")
        return
    if amount < 0 or amount > total:
        ui.gprint("SHIELD CONTROL: 'NOT THE FEDERATION TREASURY, SIR.'")
        return
    e.energy  = total - amount
    e.shields = amount
    ui.gprint(f"SHIELDS NOW AT {e.shields} UNITS.")
    ui.refresh_map()


def cmd_dam(gs, ui):
    e = gs.enterprise
    ui.gprint("DEVICE                   STATE")
    ui.gprint("-" * 33)
    for i, name in enumerate(DEVICE_NAMES):
        s      = e.damage[i]
        status = "OPERATIONAL" if s >= 0 else f"DAMAGED ({s:.2f})"
        ui.gprint(f"{name:<24} {status}")


def cmd_com(gs, ui):
    e = gs.enterprise
    if e.damage[6] < 0:
        ui.gprint("COMPUTER DAMAGED. FUNCTIONS UNAVAILABLE.")
        return
    ui.gprint("LIBRARY COMPUTER OPTIONS:")
    ui.gprint("  0  GALACTIC RECORD")
    ui.gprint("  1  STATUS REPORT")
    ui.gprint("  2  PHOTON TORPEDO DATA")
    ui.gprint("  3  STARBASE NAV DATA")
    ui.gprint("  4  DIRECTION/DISTANCE CALC")
    ui.gprint("  5  GALAXY MAP")
    try:
        opt = int(ui.ginput("OPTION: "))
    except ValueError:
        return
    fns = [_com_galaxy_record, _com_status, _com_torpedo_data,
           _com_starbase_nav, _com_direction_calc, _com_galaxy_map]
    if 0 <= opt < len(fns):
        fns[opt](gs, ui)


def _com_galaxy_record(gs, ui):
    ui.gprint("GALACTIC RECORD:")
    sep = "  +" + "-----+" * GALAXY_SIZE
    ui.gprint(sep)
    for r in range(GALAXY_SIZE):
        row = []
        for c in range(GALAXY_SIZE):
            row.append(f" {gs.galaxy[r][c]:03d} " if gs.charted[r][c] else " *** ")
        ui.gprint("  |" + "|".join(row) + "|")
        ui.gprint(sep)


def _com_status(gs, ui):
    e = gs.enterprise
    ui.gprint(f"STARDATE:           {gs.stardate}")
    ui.gprint(f"CONDITION:          {condition_str(gs)}")
    ui.gprint(f"QUADRANT:           {e.quadrant[0]+1},{e.quadrant[1]+1}")
    ui.gprint(f"SECTOR:             {e.sector[0]+1},{e.sector[1]+1}")
    ui.gprint(f"TORPEDOES:          {e.torpedoes}")
    ui.gprint(f"TOTAL ENERGY:       {e.energy+e.shields}")
    ui.gprint(f"SHIELDS:            {e.shields}")
    ui.gprint(f"KLINGONS REMAINING: {gs.klingons_remaining}")
    ui.gprint(f"STARDATES LEFT:     {gs.mission_end-gs.stardate}")


def _com_torpedo_data(gs, ui):
    e = gs.enterprise
    if not gs.klingon_positions:
        ui.gprint("SENSORS SHOW NO ENEMY SHIPS.")
        return
    ui.gprint("ENTERPRISE → KLINGON BATTLE CRUISER:")
    for kr, kc, ke in gs.klingon_positions:
        d, dist = _calc_direction(e.sector[0], e.sector[1], kr, kc)
        ui.gprint(f"  DIRECTION={d:.2f}  DISTANCE={dist:.2f}")


def _com_starbase_nav(gs, ui):
    e     = gs.enterprise
    bases = gs._find_in_grid(">!<")
    if not bases:
        ui.gprint("SPOCK: 'NO STARBASES IN THIS QUADRANT.'")
        return
    ui.gprint("ENTERPRISE → STARBASE:")
    for br, bc in bases:
        d, dist = _calc_direction(e.sector[0], e.sector[1], br, bc)
        ui.gprint(f"  DIRECTION={d:.2f}  DISTANCE={dist:.2f}")


def _com_direction_calc(gs, ui):
    ui.gprint("DIRECTION/DISTANCE CALCULATOR")
    try:
        fr = int(ui.ginput("FROM SECTOR ROW (1-8): ")) - 1
        fc = int(ui.ginput("FROM SECTOR COL (1-8): ")) - 1
        tr = int(ui.ginput("TO   SECTOR ROW (1-8): ")) - 1
        tc = int(ui.ginput("TO   SECTOR COL (1-8): ")) - 1
    except ValueError:
        ui.gprint("INVALID.")
        return
    d, dist = _calc_direction(fr, fc, tr, tc)
    ui.gprint(f"DIRECTION={d:.2f}  DISTANCE={dist:.2f}")


def _com_galaxy_map(gs, ui):
    e   = gs.enterprise
    qr, qc = e.quadrant
    ui.gprint("        THE GALAXY")
    ui.gprint("    1  2  3  4  5  6  7  8")
    sep = "   +" + "---+" * GALAXY_SIZE
    ui.gprint(sep)
    for r in range(GALAXY_SIZE):
        row = []
        for c in range(GALAXY_SIZE):
            if gs.charted[r][c]:
                k = gs.galaxy[r][c] // 100
                b = (gs.galaxy[r][c] // 10) % 10
                marker = f"{k}{b}*" if (r == qr and c == qc) else f"{k}{b} "
            else:
                marker = "..*" if (r == qr and c == qc) else ".. "
            row.append(marker)
        ui.gprint(f" {r+1} |" + "|".join(row) + "|")
        ui.gprint(sep)


# ---------------------------------------------------------------------------
# Klingon attack / docking
# ---------------------------------------------------------------------------

def _klingons_fire(gs, ui):
    e = gs.enterprise
    if e.docked or not gs.klingon_positions:
        return
    for kp in gs.klingon_positions:
        kr, kc, ke = kp
        dist = max(0.1, math.sqrt((e.sector[0] - kr) ** 2 + (e.sector[1] - kc) ** 2))
        hit  = int(ke / (dist * dist) * (random.random() * 0.5 + 0.5))
        if e.shields >= hit:
            e.shields -= hit
            ui.gprint(f"KLINGON {kc+1},{kr+1}: SHIELDS HIT -{hit} → {e.shields} LEFT")
        else:
            rem      = hit - e.shields
            e.shields = 0
            e.energy -= rem
            ui.gprint(f"KLINGON {kc+1},{kr+1}: SHIELDS BUCKLED! -{rem} HULL DAMAGE!")


def _check_docking(gs, ui):
    e = gs.enterprise
    sr, sc = e.sector
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            r2, c2 = sr + dr, sc + dc
            if 0 <= r2 < QUADRANT_SIZE and 0 <= c2 < QUADRANT_SIZE:
                if gs.quadrant_map[r2][c2] == ">!<":
                    if not e.docked:
                        e.docked    = True
                        e.shields   = 0
                        e.energy    = 3000
                        e.torpedoes = 10
                        for i in range(8):
                            e.damage[i] = 0.0
                        ui.gprint("SHIELDS DROPPED FOR DOCKING.")
                        ui.gprint("STARBASE: ALL SYSTEMS REPAIRED AND RESTOCKED.")
                    return
    e.docked = False


# ---------------------------------------------------------------------------
# Win / lose
# ---------------------------------------------------------------------------

def check_game_over(gs, ui):
    e = gs.enterprise
    if e.energy <= 0:
        ui.gprint("")
        ui.gprint("*** ENTERPRISE DESTROYED ***")
        ui.gprint("THE FEDERATION WILL BE CONQUERED.")
        return True
    if gs.klingons_remaining <= 0:
        elapsed = gs.stardate - (gs.mission_end - 25)
        ui.gprint("")
        ui.gprint("*** CONGRATULATIONS, CAPTAIN ***")
        ui.gprint(f"ALL KLINGONS DESTROYED IN {elapsed} STARDATES.")
        score = e.energy // 10 + e.torpedoes * 50
        ui.gprint(f"EFFICIENCY RATING: {score}")
        return True
    if gs.stardate >= gs.mission_end:
        ui.gprint("")
        ui.gprint("*** MISSION FAILED — TIME EXPIRED ***")
        ui.gprint(f"{gs.klingons_remaining} KLINGON SHIPS WERE NOT DESTROYED.")
        return True
    if gs.starbases_remaining <= 0 and e.energy < 1000:
        ui.gprint("")
        ui.gprint("*** MISSION FAILURE ***")
        ui.gprint("ALL STARBASES DESTROYED AND INSUFFICIENT ENERGY.")
        return True
    return False


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------

def game_main(ui):
    ui.gprint("YOUR ORDERS ARE AS FOLLOWS:")
    ui.gprint("  DESTROY THE KLINGON BATTLE GROUP")
    ui.gprint("  BEFORE THEY ATTACK FEDERATION HQ!")
    ui.gprint("")

    gs = GameState()
    ui.set_game_state(gs)

    time_left = gs.mission_end - gs.stardate
    ui.gprint(f"MISSION BEGINS IN '{gs.quadrant_name()}'.")
    ui.gprint(f"{gs.klingons_remaining} KLINGON BATTLE CRUISERS DETECTED.")
    ui.gprint(f"FEDERATION NEEDS HELP IN {time_left} STARDATES.")
    ui.gprint(f"{gs.starbases_remaining} STARBASE{'S' if gs.starbases_remaining != 1 else ''} AVAILABLE.")
    ui.gprint("")

    qr, qc = gs.enterprise.quadrant
    cell = gs.galaxy[qr][qc]
    k3   = cell // 100
    b3   = (cell // 10) % 10
    if k3 > 0:
        ui.gprint(f"COMBAT ALERT! {k3} KLINGON{'S' if k3>1 else ''} IN THIS QUADRANT!")
    if b3 > 0:
        ui.gprint("STARBASE IN THIS QUADRANT.")

    ui.refresh_map()

    commands = {
        "NAV": cmd_nav, "SRS": cmd_srs, "LRS": cmd_lrs,
        "PHA": cmd_pha, "TOR": cmd_tor, "SHE": cmd_she,
        "DAM": cmd_dam, "COM": cmd_com,
    }

    while True:
        if check_game_over(gs, ui):
            ui.wait_key()
            break

        try:
            cmd = ui.ginput("").strip().upper()
        except (EOFError, KeyboardInterrupt):
            ui.gprint("--- TRANSMISSION ENDED ---")
            break

        if cmd == "XXX":
            ui.gprint("FAREWELL, CAPTAIN. STARFLEET OUT.")
            break
        elif cmd in commands:
            commands[cmd](gs, ui)
        elif cmd in ("HELP", "?", "H"):
            ui.gprint("COMMANDS: NAV SRS LRS PHA TOR SHE DAM COM XXX")
        elif cmd:
            ui.gprint(f"UNKNOWN: '{cmd}'. TRY: NAV SRS LRS PHA TOR SHE DAM COM XXX")

        if check_game_over(gs, ui):
            ui.wait_key()
            break


# ---------------------------------------------------------------------------
# Splash screen
# ---------------------------------------------------------------------------

# ASCII Enterprise – side profile (saucer left/front, nacelle right/rear)
_SPLASH_ART = [
    r"           ,----------.  U.S.S. ENTERPRISE  NCC-1701",
    "          /  NCC-1701   \\",
    r"         |               |",
    r"   ,_____|_______________|________________________________,",
    "  /                                                        \\",
    r" |                                                          |====>",
    r"  \_____|_______________|________________________________/",
    r"         |               |",
    r"          \_____________/",
    r"                 |",
    r"          ,______|______.",
    "         /        |       \\",
    r"        (         |        )=======>",
    r"         \________|_______/",
]

_CREDITS = [
    ("Mike Mayfield  ", "Star Trek (1971)  —  SDS Sigma 7 mainframe"),
    ("Bob Leedom     ", "Super Star Trek (1974)  —  Data General Nova 800"),
    ("David Ahl      ", "Creative Computing edition (1978)  —  first 1M-copy book"),
    ("coding-horror  ", "basic-computer-games  (open-source preservation)"),
]


def show_splash(stdscr):
    """Full-screen splash with ASCII Enterprise.  Returns on any keypress."""
    H, W = stdscr.getmaxyx()

    # Initialise colour pairs (same indices GameUI reuses later)
    has_color = curses.has_colors()
    if has_color:
        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1
        except Exception:
            bg = curses.COLOR_BLACK
        curses.init_pair(1, curses.COLOR_GREEN,  bg)   # enterprise / normal
        curses.init_pair(2, curses.COLOR_RED,    bg)   # klingon / alert
        curses.init_pair(3, curses.COLOR_YELLOW, bg)   # starbase / prompt
        curses.init_pair(4, curses.COLOR_CYAN,   bg)   # borders / labels
        curses.init_pair(5, curses.COLOR_WHITE,  bg)   # stars / body text

    curses.curs_set(0)
    stdscr.erase()

    def cp(n, bold=False):
        a = curses.color_pair(n) if has_color else curses.A_NORMAL
        return a | curses.A_BOLD if bold else a

    def put(row, text, attr=curses.A_NORMAL):
        """Write centred text, silently clipping anything off-screen."""
        if row < 1 or row >= H - 1:
            return
        col = max(1, (W - len(text)) // 2)
        try:
            stdscr.addstr(row, col, text[: max(0, W - col - 1)], attr)
        except curses.error:
            pass

    # ── Outer border ────────────────────────────────────────────────────────
    try:
        stdscr.box()
    except curses.error:
        pass

    # ── Title block ─────────────────────────────────────────────────────────
    put(2, "* * *   S U P E R   S T A R   T R E K   * * *", cp(4, bold=True))
    put(3, "A  Python  Translation  of  the  Classic  1978  BASIC  Game", cp(5))

    # ── Decorative separator ─────────────────────────────────────────────────
    sep = "─" * min(60, W - 4)
    put(4, sep, cp(4))

    # ── Enterprise ASCII art ─────────────────────────────────────────────────
    # Centre the whole block on the widest line so every line shares the same
    # left-column offset — individual centering shifts shorter lines right and
    # breaks the image.
    art_start = 5
    art_col = max(1, (W - max(len(l) for l in _SPLASH_ART)) // 2)
    for i, line in enumerate(_SPLASH_ART):
        if "|====>" in line:
            attr = cp(1, bold=True)   # main hull + deflector dish — green
        elif "=======>" in line:
            attr = cp(3, bold=True)   # warp nacelle exhaust — yellow
        else:
            attr = cp(5)              # structural lines — white
        row = art_start + i
        if 1 <= row < H - 1:
            try:
                stdscr.addstr(row, art_col, line[: max(0, W - art_col - 1)], attr)
            except curses.error:
                pass

    art_end = art_start + len(_SPLASH_ART)   # first row after art

    # ── Author ───────────────────────────────────────────────────────────────
    put(art_end + 1, "Python translation by:  @joda32", cp(3, bold=True))

    # ── Credits ──────────────────────────────────────────────────────────────
    cr_start = art_end + 3
    put(cr_start, "─ ─ ─   With  Thanks  To  The  Original  Creators   ─ ─ ─", cp(4))
    for i, (who, what) in enumerate(_CREDITS):
        # Left-name in yellow, description in white — centred as a unit
        full = who + what
        col  = max(1, (W - len(full)) // 2)
        row  = cr_start + 1 + i
        if row >= H - 2:
            break
        try:
            stdscr.addstr(row, col,
                          who[: max(0, W - col - 1)],
                          cp(3, bold=True))
            stdscr.addstr(row, col + len(who),
                          what[: max(0, W - col - len(who) - 1)],
                          cp(5))
        except curses.error:
            pass

    # ── Bottom prompt ────────────────────────────────────────────────────────
    put(H - 2, "[ PRESS ANY KEY TO ENGAGE WARP DRIVE ]", cp(3, bold=True))

    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not CURSES_AVAILABLE:
        print("This game requires curses.")
        print("On Windows, run:  pip install windows-curses")
        sys.exit(1)
    try:
        def _run(stdscr):
            show_splash(stdscr)
            game_main(GameUI(stdscr))
        curses.wrapper(_run)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
