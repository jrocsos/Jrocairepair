#!/bin/bash

# Check if device is connected
adb wait-for-device

echo "[*] Enabling TalkBack Accessibility..."
# Enable TalkBack globally
adb shell settings put secure enabled_accessibility_services com.google.android.marvin.talkback/com.google.android.accessibility.talkback.TalkBackService
adb shell settings put secure accessibility_enabled 1

echo "[*] Waiting for TalkBack to initialize..."
sleep 5

# Simulate a double-tap on the "OK" button usually present in the TalkBack setup
# This varies by Android version, but generally involves sending touch events
echo "[*] Simulating Touch Events to bypass Setup Wizard..."

# Method 1: Using input tap (requires root or adb shell permissions)
adb shell input tap 500 1000  # Coordinates vary by device!
adb shell input tap 500 1000

# Method 2: The "Shizuku" method (More reliable on Android 11+)
# Requires Shizuku app installed and running via ADB
adb shell sh /storage/emulated/0/shizuku-api.sh

echo "[*] If successful, the phone should now be on the Wi-Fi screen."
echo "[*] Connect to Wi-Fi, then open Settings > Accounts > Add Account > Google"
echo "[*] Enter your Google Account credentials to lock the bypass permanently."