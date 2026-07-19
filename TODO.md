# MediKal - TODO

## Wearable sync fix (Health Dashboard → Sync Device)
1. Identify the current smartwatch “sync device” implementation.
   - Located in `frontend/lib/core/services/bluetooth_service.dart` and `frontend/lib/features/vitals/vitals_screen.dart`.
2. Replace fake/demo connection logic with a real BLE connection approach.
   - For now: keep Web Bluetooth only (Chrome/Edge) and remove any “fake” ECG/wave/placeholder UI that implies real data.
3. Ensure the sync button actually reflects BLE connection state.
   - Correctly set `_btConnected`, `_connectedDevice`, and start/stop notifications.
4. Remove extra wearable features not supported by modern watches for initial release.
   - ✅ Removed “LIVE VITAL FEED (ECG)” and ECG waveform from `frontend/lib/features/vitals/vitals_screen.dart`.
5. Add clear fallback UX for unsupported platforms.
   - If Web Bluetooth isn’t supported, show “Not Supported” dialog.

6. Test:
   - Build/run Flutter web on Chrome.
   - Verify: connectSmartwatch triggers callbacks; values update live.
   - Verify: disconnect stops live values.

