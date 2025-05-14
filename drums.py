import cv2
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector

# 🎛️ MIDI Setup
pygame.midi.init()
player = pygame.midi.Output(0)
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.85, maxHands=2)

# ⏱️ Settings
MIDI_CHANNEL = 9
TRIGGER_COOLDOWN = 0.2

# 🎯 Drum Assignments
drum_map = {
    "left": {
        "thumb": (38, "Snare"),
        "index": (41, "Low Tom"),
        "middle": (47, "Mid Tom"),
        "ring": (45, "Tom"),
        "pinky": (42, "Hi-Hat")
    },
    "right": {
        "thumb": (36, "Bass"),
        "index": (51, "Ride Cymbal"),
        "middle": (49, "Crash 1"),
        "ring": (57, "Crash 2"),
        "pinky": (55, "Splash")
    }
}

# 🧠 State Tracking
last_trigger = {
    hand: {finger: 0 for finger in drum_map[hand]} for hand in drum_map
}
prev_state = {
    hand: {finger: 0 for finger in drum_map[hand]} for hand in drum_map
}

# 🎵 Trigger Drum
def trigger(note):
    player.write_short(0x99, note, 127)

# 🖼️ Main Loop
while True:
    success, img = cap.read()
    if not success:
        continue

    hands, img = detector.findHands(img, draw=True)
    current_time = time.time()

    if hands:
        for hand in hands:
            hand_type = "left" if hand["type"] == "Left" else "right"
            if hand_type not in drum_map:
                continue

            fingers = detector.fingersUp(hand)
            finger_names = ["thumb", "index", "middle", "ring", "pinky"]
            center_x, center_y = hand["center"]

            for i, finger in enumerate(finger_names):
                if finger in drum_map[hand_type]:
                    note, label = drum_map[hand_type][finger]
                    is_up = fingers[i]
                    was_up = prev_state[hand_type][finger]

                    if is_up and not was_up:
                        if current_time - last_trigger[hand_type][finger] > TRIGGER_COOLDOWN:
                            trigger(note)
                            last_trigger[hand_type][finger] = current_time

                    if is_up:
                        offset = (i - 2) * 30
                        cv2.putText(img, label, (center_x + 40, center_y + offset),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                    prev_state[hand_type][finger] = is_up

    cv2.imshow("🥁 Optimized Drum Kit", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 🧹 Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.midi.quit()
