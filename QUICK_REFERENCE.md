# Quick Reference: New Features

## 🎯 What Was Implemented

### 1. **Music Plays Between Levels** ✓
- Music now plays automatically when you load a new level
- Each level gets its assigned music with correct BPM
- Smooth fade-out/fade-in between tracks

### 2. **Coins Drop from Enemies** ✓
- When you defeat enemies, they drop 5 coins
- Each coin worth 1-3 gold randomly
- Coins spray outward in a satisfying arc

### 3. **Coins Bob Up and Down** ✓
- Coins have a smooth bobbing animation (up/down wave)
- Bobbing continues while coins are airborne and at rest
- Makes coins visually attractive and easy to spot

### 4. **Collect Coins for Gold** ✓
- Walk into a coin to pick it up
- Gold is instantly added to your inventory
- Console shows pickup message: "Picked up X gold! Total: Y"

### 5. **Gold System** ✓
- Your character now has a `gold` attribute
- Starts at 0
- Increases when collecting coins
- Ready to be used for shops, rewards, etc.

### 6. **Rhythm Circle Syncs to New Music** ✓
- When you change levels, the rhythm circle resets
- It automatically syncs to the new song's BPM
- Beat indicators will be accurate for the new music

---

## 📝 How to Use

### Checking Gold
```python
# In game code:
print(f"Player has {self.player.gold} gold")

# Add gold manually:
self.player.gold += 10
```

### Customizing Coins
```python
# In _spawn_enemy_drops():
coin = Coin(x, y, gold_value=5)  # Make coins worth more
```

### Adding More Coins
```python
def _spawn_enemy_drops(self, enemy, count=10):  # Drop 10 instead of 5
    # ... rest of code
```

---

## 🔧 Technical Notes

### Coin Class Properties
- `coin.rect` - Position and size
- `coin.gold_value` - How much gold it gives
- `coin.vx, coin.vy` - Physics velocity
- `coin.life` - Time until despawn (3 seconds default)
- `coin.bob_timer` - Bobbing animation state

### Coin Lifecycle
1. Enemy dies → Coins spawn at enemy location
2. Coins spray outward with physics
3. Coins bob up/down during flight and on ground
4. Player walks into coin
5. Coin removed, gold added to player
6. Or coin expires after 3 seconds

### Music System
- Music ID → Song object with auto-detected BPM
- BPM used for rhythm circle calculations
- Circle resets when song changes to ensure accuracy

---

## ⚡ Performance Notes

- Coin physics runs every frame (negligible CPU cost)
- Bobbing animation uses sine wave (no extra calculations beyond standard math)
- Pickup detection is simple rect collision (fast)
- Music loading is cached (no repeated loads)

---

## 🎮 Player Experience

### What Player Sees
1. Defeat an enemy
2. 5 coins spray out in a fan pattern
3. Coins gently bob up and down
4. Walk over a coin to collect it
5. Gold counter increases
6. Coins despawn after 3 seconds if not collected

### What Makes It Feel Good
- Physics arc (natural-looking spray)
- Bobbing animation (eye-catching)
- Gold feedback (confirms pickup)
- Multiple coins per enemy (rewards for victory)

---

## 📊 Default Values

```python
# Coin spawn
- Count: 5 coins per enemy
- Value: 1-3 gold each
- Spray angle: -126° to -54° (mostly upward)
- Spray speed: 300-500 pixels/second

# Bobbing
- Speed: 3.0 cycles per second
- Height: 8 pixels up/down
- Type: Smooth sine wave

# Physics
- Gravity: 800 pixels/second²
- Air resistance: 92% per frame (0.92 damping)
- Lifetime: 3 seconds before despawn
```

---

## 🐛 Troubleshooting

**Coins not appearing?**
- Check if enemies are being spawned
- Verify coins aren't being cleared by level transitions
- Make sure `_spawn_enemy_drops()` is being called

**Gold not increasing?**
- Check player collision rect size
- Verify coin pickup logic in `_update_drops()`
- Look for console error messages

**Music not playing?**
- Check `Assets/Music/` folders have correct files
- Verify song ID exists in SONGS dict
- Look for BPM detection messages in console

**Rhythm circle not syncing?**
- Confirm `reset_beat_tracking()` is being called
- Check audio_system has a current_song loaded
- Verify BPM is being detected correctly

---

## 🚀 Future Expansion Ideas

1. **Sound Effects**: Play ping sound on coin pickup
2. **Animation**: Coins float to player when collected
3. **Persistence**: Save gold in save_data.json
4. **Shop**: Use gold to buy items/upgrades
5. **Rare Coins**: Special coins worth more gold
6. **Coin Trails**: Visual effects following coins
7. **Gold Counter**: Display gold amount on screen
8. **Combo Multiplier**: More gold for harder hits

---

## ✅ Verification

All features have been tested and verified working:
- [x] Coins drop from enemies
- [x] Coins have bobbing animation
- [x] Coins can be picked up
- [x] Gold is added to player
- [x] Music plays on level transitions
- [x] Rhythm circle syncs to new BPM
- [x] No syntax errors
- [x] Backward compatible with existing code
