# 🟢 Ben 10 Run – Enhanced Edition

A side-scrolling endless runner game built with Python and Pygame, featuring classic Ben 10 aliens, synthesized sound effects, multiple scenes, and pixel-art style sprites.

---

## 📋 Requirements

- Python 3.10+
- pygame 2.6+
- numpy

Install dependencies with:

```bash
pip install pygame numpy

```

---

## 🚀 How to Run

```bash
python ben10_run_enhanced.py
```

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `SPACE` / `↑` | Jump |
| `←` / `A` | Move left lane |
| `→` / `D` | Move right lane |
| `↓` / `S` | Slide |
| `T` | Transform alien (Omnitrix) |
| `ESC` | Quit |

---

## 👾 Playable Aliens

Each alien has unique speed and jump bonuses, plus a special power:

| Alien | Power | Speed Bonus | Jump Bonus |
|-------|-------|-------------|------------|
| Ben | Human | 0 | 0 |
| Heatblast | Fire Shield | +2 | 0 |
| Four Arms | Super Punch | 0 | +2 |
| Diamondhead | Crystal | +1 | +1 |
| XLR8 | Speed Dash | +5 | 0 |
| Ghostfreak | Phase (Shield) | 0 | +3 |
| Upgrade | Tech Boost | +3 | +1 |

> 💡 **Tip:** Transforming into **Ghostfreak** activates a temporary shield that destroys one obstacle!

---

## 🌍 Scenes

The game cycles through 5 unique environments as you run:

1. Bellwood City
2. Mt. Rushmore
3. Null Void
4. Galactic Forest
5. Alien City

---

## 🔊 Sound Effects

All sounds are procedurally synthesized at startup using numpy waveforms — no audio files needed:

- Jump, Land, Slide
- Coin collect
- Hit, Shield break
- Alien transform
- Game over
- Menu blip

---

## 🪙 Scoring

- Distance traveled earns points automatically
- Collecting coins gives **+50 points** each
- Speed increases as your score grows (capped at 22)
- High score is tracked per session

---

## ❤️ Lives

You start with **3 lives**. Each obstacle hit costs one life. After a hit, you get a brief invincibility window. Lose all 3 lives and it's game over.

---

## 🐛 Known Fix (v1.1)

**Issue:** `ValueError: Array must be 2-dimensional for stereo mixer`

**Fix applied:**
- Mixer initialized in stereo mode: `pygame.mixer.pre_init(44100, -16, 2, 512)`
- All sound arrays reshaped to 2D stereo: `np.column_stack([data, data])`

---

## 📁 File Structure

```
ben10_run_enhanced.py   # Main game file (single file, no assets needed)
README.md               # This file
```

---

## 👨‍💻 Author

Made by **Nishchal Soni**

---

## 📄 License

Fan-made project for educational/personal use. Ben 10 and related characters are property of Cartoon Network / Warner Bros.
