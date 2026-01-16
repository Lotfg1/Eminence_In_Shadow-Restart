# 🎵 Rhythm Battle System - User Guide

## Overview
Your game now features a **rhythm-based combat system** where attacks become more powerful when timed to the music's beat!

## How It Works

### 🎯 Attack Timing
When you press the **SPACE** key to attack, the system checks how close you are to the beat:

- **PERFECT** (±80ms): 🟡 **+50% damage** bonus
- **GOOD** (±150ms): 🟢 **+20% damage** bonus  
- **MISS** (±250ms): 🔴 **-20% damage** penalty

### 🔥 Combo System
Chain attacks with good timing to build a combo:
- Each successful hit adds to your combo counter
- **+10% damage per combo hit** (max +50% at 5 hits)
- Combo multiplier **stacks** with timing multiplier!
- Missing a beat or waiting too long (2 seconds) breaks the combo

### 💪 Attack Types
Hold different directions while attacking for different moves:

1. **Neutral Attack** (no direction)
   - Standard damage and knockback
   - Best for basic combos

2. **Forward Attack** (hold A or D)
   - +20% base damage
   - +50% knockback
   - Great for pushing enemies back

3. **Down Attack** (hold S)
   - +10% base damage
   - Less knockback (sweeps enemies)
   - Good for low hits

## Visual Feedback

### Beat Timing Bar (Bottom Center)
- Shows when to attack for perfect timing
- **Red line** = current position in the beat
- **Gold center** = perfect timing window
- **Green area** = good timing window

### Accuracy Display (Above Player)
- Shows "PERFECT", "GOOD", or "MISS" after each attack
- Text floats upward and fades
- Color-coded for instant feedback

### Combo Counter (Top Right)
- Shows current combo count
- Displays total damage multiplier
- Only visible when you have an active combo

### Attack Slash Effect
- Visual slash appears when attacking
- **Blue** = Neutral attack
- **Gold** = Forward attack  
- **Red** = Down attack

## Pro Tips

1. **Watch the beat bar** - Attack when the red line crosses the gold center
2. **Listen to the music** - The beat bar syncs with the rhythm
3. **Build combos** - Don't spam! Time each attack for maximum damage
4. **Mix attack types** - Use forward attacks for knockback, down for sweeps
5. **Perfect timing matters** - A perfect 5-hit combo does **2.25x damage**!

## Damage Calculation Example

Base damage: 15
- Forward attack: 15 × 1.2 = **18 base**
- Perfect timing: 18 × 1.5 = **27 damage**
- 5-hit combo: 27 × 1.5 = **40.5 damage** (wow!)

Without rhythm: 15 damage  
With perfect rhythm combo: 40+ damage

**That's almost 3x more damage for good rhythm!**

## Controls

- **SPACE** - Attack (primary attack button)
- **A/D** - Move left/right (hold while attacking for forward attack)
- **S** - Down (hold while attacking for down attack)
- **F** - Block
- **W** - Jump/Teleport
- **E** - Interact
- **ESC** - Pause

## Settings

You can adjust the rhythm system in `Assets/RhythmBattle.py`:
- Timing window sizes
- Damage multipliers
- Visual feedback colors
- Combo timeout duration

Enjoy your rhythm-based battles! 🎮🎵
