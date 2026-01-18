import pygame
import random
import time
import cv2
import mediapipe as mp
from collections import deque

# ================== SETUP ==================
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Controlled Snake Game 🐍")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

eat_sound = pygame.mixer.Sound("assets/eat.wav")

# ================== GAME VARIABLES ==================
snake = [(320,240), (300,240), (280,240)]
direction = "RIGHT"
score = 0

speed = 8           # snake speed (smooth)
move_delay = 0.15   # movement delay
last_move_time = time.time()

food = (random.randrange(0, WIDTH, 20), random.randrange(0, HEIGHT, 20))

GAME_TIME = 60
start_time = time.time()

# ================== CAMERA SETUP ==================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

prev_positions = deque(maxlen=5)

# ================== HAND DIRECTION ==================
def get_direction():
    ret, frame = cap.read()
    if not ret:
        return None

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    cv2.imshow("Camera - Move Index Finger", frame)
    cv2.waitKey(1)

    if result.multi_hand_landmarks:
        lm = result.multi_hand_landmarks[0].landmark[8]
        x = int(lm.x * WIDTH)
        y = int(lm.y * HEIGHT)

        prev_positions.append((x, y))
        if len(prev_positions) < 5:
            return None

        dx = prev_positions[-1][0] - prev_positions[0][0]
        dy = prev_positions[-1][1] - prev_positions[0][1]

        if abs(dx) > abs(dy):
            if dx > 20: return "RIGHT"
            if dx < -20: return "LEFT"
        else:
            if dy > 20: return "DOWN"
            if dy < -20: return "UP"

    return None

# ================== GAME LOOP ==================
running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Timer
    time_left = int(GAME_TIME - (time.time() - start_time))
    if time_left <= 0:
        break

    # Update direction from hand
    new_dir = get_direction()
    if new_dir:
        direction = new_dir

    # Auto move snake
    if time.time() - last_move_time > move_delay:
        last_move_time = time.time()

        x, y = snake[0]
        if direction == "UP": y -= 20
        if direction == "DOWN": y += 20
        if direction == "LEFT": x -= 20
        if direction == "RIGHT": x += 20

        # ===== BOUNCE LOGIC =====
        if x < 0:
            x = 0
            direction = "RIGHT"
        elif x > WIDTH - 20:
            x = WIDTH - 20
            direction = "LEFT"

        if y < 0:
            y = 0
            direction = "DOWN"
        elif y > HEIGHT - 20:
            y = HEIGHT - 20
            direction = "UP"

        new_head = (x, y)
        snake.insert(0, new_head)

        if new_head == food:
            score += 1
            eat_sound.play()
            food = (random.randrange(0, WIDTH, 20), random.randrange(0, HEIGHT, 20))
        else:
            snake.pop()

    # Draw snake
    for part in snake:
        pygame.draw.rect(screen, (0, 255, 0), (*part, 20, 20))

    # Draw food
    pygame.draw.rect(screen, (255, 0, 0), (*food, 20, 20))

    # UI
    screen.blit(font.render(f"Time: {time_left}", True, (255,255,255)), (10,10))
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10,40))

    pygame.display.update()
    clock.tick(60)

# ================== CLEAN EXIT ==================
pygame.quit()
cap.release()
cv2.destroyAllWindows()
