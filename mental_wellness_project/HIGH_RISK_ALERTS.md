# High Risk Alert Features

## ✅ Features Added

### 1. **Browser Notifications for High Risk**
- Shows notification popup when high/critical risk is detected
- Works even when page is visible (not just when minimized)
- Includes alert message and suggested actions
- Notification stays visible until user interacts (10 second timeout)
- Clicking notification focuses the browser window

### 2. **Text-to-Speech Voice Alerts**
- Speaks the alert message automatically
- Announces risk level: "HIGH ALERT" or "CRITICAL ALERT"
- Reads the detected issues
- Speaks suggested actions to reduce risk
- Uses natural-sounding voice (if available)
- Prevents repetition of same alert

## How It Works

### When High Risk is Detected:

1. **Visual Alert** (on page)
   - Red alert box appears in "Emergency Alerts" section
   - Shows risk level and detected issues

2. **Browser Notification** (popup)
   - System notification appears
   - Shows title: "HIGH ALERT" or "CRITICAL ALERT"
   - Includes message and suggested actions
   - Stays visible until clicked or 10 seconds

3. **Voice Announcement** (speaker)
   - Speaks: "High alert. HIGH risk detected."
   - Reads the detected issues
   - Announces: "Here are some suggestions to reduce the risk:"
   - Speaks each suggestion one by one

## Example Voice Output

When high risk is detected, you'll hear:

```
"High alert. HIGH risk detected. 
Elevated stress levels detected across multiple indicators. 
Here are some suggestions to reduce the risk:
Suggestion 1: Take a short mindful walk outside.
Suggestion 2: Try the 4-7-8 breathing technique for two minutes.
Suggestion 3: Write down three things you can control right now."
```

## Browser Compatibility

### Notifications
- ✅ Chrome/Edge: Full support
- ✅ Firefox: Full support
- ✅ Safari: Limited support
- ⚠️ Requires permission (requested automatically)

### Text-to-Speech
- ✅ Chrome/Edge: Full support
- ✅ Firefox: Full support
- ✅ Safari: Full support
- ✅ Works without permission (built-in browser feature)

## Permissions

### Notification Permission
- Browser will ask for notification permission when you start monitoring
- Click "Allow" to enable notifications
- If denied, notifications won't show but voice alerts still work

### Text-to-Speech
- No permission needed
- Uses browser's built-in speech synthesis
- Works automatically

## Customization

### Voice Settings
The system uses:
- **Rate**: 0.9 (slightly slower for clarity)
- **Pitch**: 1.0 (normal)
- **Volume**: 1.0 (maximum)
- **Language**: English (US)
- **Voice**: Automatically selects best available voice

### Alert Prevention
- Same alert won't repeat (prevents spam)
- Alerts are tracked by content
- New alerts will trigger new notifications/speech

## Testing

### To Test High Risk Alert:

1. **Start monitoring**
2. **Wait for analysis** (15 seconds)
3. **If risk is low/medium**: No alert
4. **If risk is high/critical**: 
   - ✅ Alert box appears
   - ✅ Notification popup appears
   - ✅ Voice speaks the alert

### Manual Test (for development):
You can temporarily modify the risk level in the backend to test alerts.

## Troubleshooting

### Notifications Not Showing
- Check browser notification permission (click lock icon → Site settings)
- Make sure notifications are enabled in browser settings
- Try refreshing the page

### Voice Not Speaking
- Check browser console for errors (F12)
- Make sure system volume is not muted
- Try a different browser (Chrome/Edge recommended)
- Check if speech synthesis is supported: `"speechSynthesis" in window`

### Voice Too Fast/Slow
- The rate is set to 0.9 (slightly slower)
- Can be adjusted in code if needed

### Alerts Repeating
- System prevents duplicate alerts
- If same alert appears multiple times, check backend logs
- Each unique alert will trigger once

## Code Location

- **Notifications**: `showHighRiskNotification()` function
- **Text-to-Speech**: `speakHighRiskAlert()` function
- **Trigger**: `renderMonitorResult()` function (when risk_level is "high" or "critical")

## Security & Privacy

- ✅ All processing happens locally in browser
- ✅ No external services used
- ✅ No data sent to third parties
- ✅ Voice synthesis uses browser's built-in engine
- ✅ Notifications are browser-native (secure)

## Future Enhancements

Possible improvements:
- Custom voice selection
- Adjustable speech rate/pitch
- Multiple language support
- Alert sound effects
- Alert history log

