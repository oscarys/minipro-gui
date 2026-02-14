# T48 MiniPro GUI - Quick Reference Card (v1.3.3)

## 🚀 Quick Start (3 Steps)

1. **Connect & Detect**
   - Device Info → "Detect Programmer"

2. **Select Your Chip**
   - Click dropdown → Type device name (e.g., "AT29")
   - Or pick from 40+ pre-loaded common devices
   - Or click "Load Device List" for all 13,000+

3. **Read or Write**
   - Read/Write tab → Choose operation
   - Files auto-filled from last session
   - Watch real-time progress bar!

---

## 📖 Common Workflows

### Read Firmware from Chip
```
1. Device dropdown (remembered from last time!)
   └─ Select or type "AT29C256@DIP28"
   
2. Read/Write tab
   └─ Memory Type: "code"
   └─ Output File: Already filled in!
   └─ Click "Read Device"
   └─ Watch progress: 0% → 50% → 100%
   └─ Check console for success ✓
```

### Write Firmware to Chip
```
1. Device dropdown
   └─ Select "AT29C256@DIP28"
   └─ Click "Read Chip ID" (verify chip)
   
2. Read/Write tab
   └─ Input File: Already filled in!
   └─ Click "Erase Device" (quick erase!)
   └─ Click "Write to Device"
   └─ Watch progress: Writing: 0% → 100%
   └─ Verify success in console
```

### Flash SPI Memory (e.g., W25Q32)
```
1. Device dropdown
   └─ Type "W25Q32" → Select "W25Q32JV@SOIC8"
   
2. Configuration tab
   └─ SPI Clock: "30" MHz
   
3. Read/Write tab
   └─ Input File: Browse or use remembered
   └─ Click "Write to Device"
   └─ Watch: Writing: 0% → 50% → 100%
```

### Quick Erase & Write
```
1. Device already selected
2. Read/Write tab
   └─ Click "Erase" (watch progress!)
   └─ Click "Write" (watch progress!)
   └─ Done! All in one tab
```

---

## 🎯 Tab Functions

### Device Info
- **Detect Programmer** → Check T48 connection
- **Device Dropdown** → Type to search, select from 40+ common devices
- **Load Device List** → Fetch all 13,000+ devices (background)
- **Get Device Info** → View specs & voltages
- **Read Chip ID** → Verify chip is correct
- **Pin Contact Check** → Test physical connection
- **Blank Check** → Verify chip is erased

### Read/Write
- **Memory Type** → code/data/config/user
- **File Format** → binary/ihex/srec
- **Read Device** → Save chip contents to file
- **Write to Device** → Program chip from file
- **Verify Device** → Compare chip to file
- **Erase Device** → Quick erase button! ⚡

### Firmware/Erase
- **Erase Device** → Wipe chip (⚠️ permanent!)
- **Update Firmware** → Flash T48 programmer

### Configuration
- **VPP** → Programming voltage (9-25V)
- **VDD** → Write voltage (3.3-6.5V)
- **VCC** → Verify voltage (3.3-6.5V)
- **SPI Clock** → Speed for SPI chips (4-30MHz)
- **Pulse Delay** → Programming timing
- **Protection** → Enable/disable write protect
- **ICSP** → In-circuit programming options

### Advanced
- **Logic Test** → Test RAM/Logic ICs
- **Auto-Detect** → Find SPI chip type
- **Custom Command** → Run any minipro command

### Console (Bottom)
- **Clear Console** → Clean output
- **Debug Mode** → Show progress parsing 🔍
- **Progress Bar** → Real-time updates 📊

---

## ⚙️ Settings Cheat Sheet

### Common Chip Voltages

| Chip Type | VPP | VDD | VCC |
|-----------|-----|-----|-----|
| 27C EPROM | 12-14V | 5V | 5V |
| 29C EEPROM | Default | 5V | 5V |
| SPI Flash | Default | 3.3V | 3.3V |
| AVR/PIC | 12V | 5V | 5V |

### SPI Flash Settings
- **Standard**: 8 MHz
- **Fast**: 15 MHz  
- **Maximum**: 30 MHz

### Memory Types Explained
- **code** → Program/firmware (most common)
- **data** → EEPROM data
- **config** → Fuse bits, lock bits
- **user** → User signature/ID
- **calibration** → Factory trim (read-only)

---

## 🔧 Checkbox Quick Ref

### Read/Write Tab
- ☑️ **Skip ID Check** → Ignore chip ID during read
- ☑️ **Skip Erase** → Don't erase before write (faster)
- ☑️ **Skip Verify** → Don't verify after write (not recommended)
- ☑️ **No ID Error** → Ignore ID mismatch warnings
- ☑️ **No Size Error** → Ignore file size warnings

### Configuration Tab
- ☑️ **Unprotect** → Remove write protection before programming
- ☑️ **Protect** → Enable write protection after programming
- ☑️ **Use ICSP (VCC)** → In-circuit programming with power
- ☑️ **Use ICSP (no VCC)** → In-circuit programming without power

---

## 🚨 Warning Messages

### ⚠️ "Device ID mismatch"
→ Wrong chip or bad contact → Check insertion

### ⚠️ "File size mismatch"  
→ File doesn't match chip size → Verify file

### ⚠️ "Verification failed"
→ Write didn't succeed → Try again, check voltages

### ⚠️ "No programmer found"
→ T48 not detected → Check USB, drivers, permissions

---

## 🎨 Console Colors & Progress

### Console Colors
- 🔵 **Cyan** → Command being run
- ⚪ **White** → Normal output
- 🟣 **Purple** → Debug parsing info (when enabled)
- 🟢 **Green** → Success ✓
- 🔴 **Red** → Error/Warning ✗

### Progress Bar
- 📊 **Real-time updates** → 0% → 25% → 50% → 100%
- 🏷️ **Operation label** → "Reading: 50%", "Writing: 75%"
- ⏱️ **Auto-hide** → Disappears after completion
- 🔍 **Debug mode** → Enable to see parsing details

### Debug Mode Features
Enable "Debug Mode" checkbox to see:
- `[PARSE]` → Raw minipro output lines
- `[PROGRESS]` → What parser detected
- Percentage calculations in real-time
- Helps troubleshoot progress issues

---

## 💡 Pro Tips

### Smart Workflow
- ✅ **Device remembered** from last session
- ✅ **Files auto-filled** from previous use
- ✅ **Directory remembered** for file browser
- ✅ **Settings persist** between launches
- ✅ **One-tab workflow** Erase → Write → Verify

### Using Debug Mode
1. Enable when testing new devices
2. Watch purple `[PARSE]` lines in real-time
3. See `[PROGRESS]` percentage detections
4. Disable for normal use (less clutter)

### Device Selection
- Type partial name: "W25Q" finds all W25Q chips
- Common devices pre-loaded instantly
- Click "Load Device List" only when needed
- Selection saves automatically

### Before Writing
1. ✓ Device already selected (remembered!)
2. ✓ Read chip ID first
3. ✓ Blank check if new
4. ✓ File path already filled in
5. ✓ Watch real-time progress
6. ✓ Enable verify (don't skip!)

### After Writing  
1. ✓ Check console for success
2. ✓ Watch progress complete at 100%
3. ✓ Read back to verify (optional)
4. ✓ Enable protection if needed

### For SPI Flash
- Always set correct SPI clock speed
- Use 30MHz for fastest programming
- Some chips need lower speeds (check datasheet)
- Progress bar shows exact percentage

### Quick Operations
- Use Erase button right in Read/Write tab
- No need to switch to Firmware tab
- Watch progress in real-time
- Confirmation dialog prevents accidents

### Troubleshooting Progress
1. Enable Debug Mode checkbox
2. Run operation
3. Look for purple `[PARSE]` lines
4. Should see: `[PROGRESS] Percentage: XX%`
5. If not appearing, update to v1.3.3+

---

## 🎯 Keyboard Shortcuts

(Standard PyQt shortcuts)

- **Ctrl+Q** → Quit application
- **Ctrl+W** → Close window
- **Ctrl+Tab** → Next tab
- **Ctrl+Shift+Tab** → Previous tab

---

## 📝 File Extensions

- **.bin** → Raw binary (most common)
- **.hex** → Intel HEX format
- **.srec** → Motorola S-Record
- **.dat** → Firmware update file
- **.conf** → Config/fuses (text format)

---

## 🔗 Quick Links

- Man page: `man minipro`
- Device list: Click "List All Devices"
- Search: Enter partial name + "Search"
- Help: See README.md for full guide

---

## 📞 Emergency Commands

If GUI fails, use terminal:

```bash
# Read chip ID only
minipro -p "AT29C256@DIP28" -D

# Read everything
minipro -p "AT29C256@DIP28" -r backup.bin

# Write with verify
minipro -p "AT29C256@DIP28" -w firmware.bin

# Force erase
minipro -p "AT29C256@DIP28" -E
```

---

**Version 1.3.3** • Real-time progress updates • Compatible with minipro 0.6+ and T48

## 🆕 What's New in v1.3.3

- 📊 **Real-time progress bar** - Updates smoothly during operations
- 🔍 **Debug mode** - See exactly what's being parsed
- 🎯 **Searchable dropdown** - Type to filter 13,000+ devices
- 💾 **Persistent settings** - Remember everything between sessions
- ⚡ **Quick erase button** - Right in Read/Write tab
- 🎨 **Improved UI** - Cleaner, faster, smarter
