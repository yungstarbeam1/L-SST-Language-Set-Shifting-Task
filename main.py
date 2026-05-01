import pygame
import random
import math

from ui.card import Card
from engine.stimuli import STIMULI
from engine.trial_generator import generate_trial
from engine.lsst_logic import LSSTEngine
from settings import RULES, TRIALS_PER_RULE, SHUFFLE_RULES

pygame.init()

# ─── THEMES ────────────────────────────────────────────────────────────────
LIGHT_THEME = {
    "bg": (255, 255, 255),
    "text": (0, 0, 0),
    "card_bg": (230, 230, 230),
    "overlay": (255, 255, 255, 180)
}

DARK_THEME = {
    "bg": (30, 30, 30),
    "text": (240, 240, 240),
    "card_bg": (50, 50, 50),
    "overlay": (0, 0, 0, 180)
}

current_theme = LIGHT_THEME
is_dark_mode = False

# ─── ENGINE & STATE ────────────────────────────────────────────────────────
STATE_START = 0
STATE_PLAYING = 1
STATE_RESULTS = 2
game_state = STATE_START

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("L-SST")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)
hint_font = pygame.font.Font(None, 32)

CURSOR_HAND  = pygame.SYSTEM_CURSOR_HAND
CURSOR_ARROW = pygame.SYSTEM_CURSOR_ARROW

engine = LSSTEngine()

# Rule Logic with Optional Shuffling
rule_order = RULES[:]
if SHUFFLE_RULES:
    random.shuffle(rule_order)

rule_index = 0
current_rule = rule_order[rule_index]
consecutive_correct = 0
trial_number = 0

feedback = None
feedback_time = 0
show_feedback = False
show_debug = False
trial_start_time = 0

# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────

def handle_selection(selected_card):
    global consecutive_correct, trial_number, feedback, show_feedback, feedback_time
    correct = engine.check(target_card, selected_card, current_rule)
    trial_number += 1
    
    if correct:
        consecutive_correct += 1
    else:
        consecutive_correct = 0   

    feedback = "correct" if correct else "incorrect"
    show_feedback = True
    feedback_time = pygame.time.get_ticks()

def build_cards(target_data, choice_data):
    target_rect = pygame.Rect((WIDTH - 200) // 2, (HEIGHT - 100) // 2 - 200, 200, 100)
    target = Card(target_data["text"], target_data["semantic"], target_data["syntactic"], target_data["syllables"], target_rect)
    
    x_positions = [WIDTH // 2 - 300, WIDTH // 2 - 100, WIDTH // 2 + 100]
    choices = []
    for i, c in enumerate(choice_data):
        rect = pygame.Rect(x_positions[i], HEIGHT - 200, 180, 100)
        choices.append(Card(c["text"], c["semantic"], c["syntactic"], c["syllables"], rect))
    return target, choices

def draw_start_screen(surface, w, h, theme):
    surface.fill(theme["bg"])
    title_font = pygame.font.Font(None, 150)
    
    title_text = "L-SST"
    total_width = title_font.size(title_text)[0]
    current_x = (w - total_width) // 2
    current_time = pygame.time.get_ticks()
    
    for i, char in enumerate(title_text):
        offset = math.sin(current_time / 500 + i * 0.5) * 15
        char_surf = title_font.render(char, True, theme["text"])
        char_rect = char_surf.get_rect(center=(current_x + char_surf.get_width() // 2, (h // 2 - 50) + offset))
        surface.blit(char_surf, char_rect)
        current_x += char_surf.get_width()

    start_surf = font.render("Press SPACE to Start", True, theme["text"])
    surface.blit(start_surf, start_surf.get_rect(center=(w // 2, h // 2 + 50)))

    hint_color = (150, 150, 150)
    hint_text = " [D] for Dark Mode  |   [B] for debug display"
    hint_surf = hint_font.render(hint_text, True, hint_color)
    surface.blit(hint_surf, hint_surf.get_rect(center=(w // 2, h // 2 + 150)))

def draw_feedback(surface, w, h, state, theme):
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill(theme["overlay"])
    surface.blit(overlay, (0, 0))
    cx, cy = w // 2, h // 2
    radius = 60
    if state == "correct":
        pygame.draw.circle(surface, (46, 204, 113), (cx, cy), radius)
        pygame.draw.lines(surface, (255, 255, 255), False, [(cx - 25, cy), (cx - 5, cy + 20), (cx + 30, cy - 20)], 10)
    else:
        pygame.draw.circle(surface, (231, 76, 60), (cx, cy), radius)
        pygame.draw.line(surface, (255, 255, 255), (cx-20, cy-20), (cx+20, cy+20), 10)
        pygame.draw.line(surface, (255, 255, 255), (cx+20, cy-20), (cx-20, cy+20), 10)

def draw_results_screen(surface, w, h, total_trials, theme):
    surface.fill(theme["bg"])
    title_font = pygame.font.Font(None, 80)
    res_font = pygame.font.Font(None, 50)
    title_surf = title_font.render("TASK COMPLETE", True, theme["text"])
    surface.blit(title_surf, title_surf.get_rect(center=(w // 2, h // 2 - 100)))
    trials_surf = res_font.render(f"Total Trials: {total_trials}", True, theme["text"])
    surface.blit(trials_surf, trials_surf.get_rect(center=(w // 2, h // 2)))
    exit_surf = res_font.render("Press ESC to exit", True, theme["text"])
    surface.blit(exit_surf, exit_surf.get_rect(center=(w // 2, h // 2 + 100)))

# ─── INITIAL SETUP ─────────────────────────────────────────────────────────
target_data, choice_data = generate_trial(STIMULI, current_rule)
target_card, choice_cards = build_cards(target_data, choice_data)

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_b:
                show_debug = not show_debug
            if event.key == pygame.K_d:
                is_dark_mode = not is_dark_mode
                current_theme = DARK_THEME if is_dark_mode else LIGHT_THEME
            
            if game_state == STATE_START and event.key == pygame.K_SPACE:
                game_state = STATE_PLAYING
                trial_start_time = pygame.time.get_ticks()
            elif game_state == STATE_PLAYING and not show_feedback:
                idx = -1
                if event.key == pygame.K_1: idx = 0
                if event.key == pygame.K_2: idx = 1
                if event.key == pygame.K_3: idx = 2
                if 0 <= idx < len(choice_cards):
                    handle_selection(choice_cards[idx])

        if game_state == STATE_PLAYING and not show_feedback and event.type == pygame.MOUSEBUTTONDOWN:
            for card in choice_cards:
                if card.is_clicked(mouse_pos):
                    handle_selection(card)

    if game_state == STATE_START:
        draw_start_screen(screen, WIDTH, HEIGHT, current_theme)
    elif game_state == STATE_RESULTS:
        draw_results_screen(screen, WIDTH, HEIGHT, trial_number, current_theme)
    elif game_state == STATE_PLAYING:
        screen.fill(current_theme["bg"])
        any_hover = not show_feedback and any(c.is_hovered(mouse_pos) for c in choice_cards)
        pygame.mouse.set_cursor(CURSOR_HAND if any_hover else CURSOR_ARROW)
        
        label = font.render("TARGET", True, current_theme["text"])
        screen.blit(label, label.get_rect(center=(target_card.rect.centerx, target_card.rect.top - 40)))
        target_card.draw(screen, font, theme=current_theme)

        for i, card in enumerate(choice_cards):
            hovered = not show_feedback and card.is_hovered(mouse_pos)
            card.draw(screen, font, theme=current_theme, hovered=hovered)
            num_label = font.render(str(i + 1), True, current_theme["text"])
            screen.blit(num_label, (card.rect.centerx - 10, card.rect.top - 40))

        if show_feedback:
            draw_feedback(screen, WIDTH, HEIGHT, feedback, current_theme)
            if pygame.time.get_ticks() - feedback_time > 600:
                show_feedback = False
                if consecutive_correct >= TRIALS_PER_RULE:
                    consecutive_correct = 0
                    rule_index += 1
                    if rule_index >= len(rule_order):
                        game_state = STATE_RESULTS
                    else:
                        current_rule = rule_order[rule_index]
                
                if game_state == STATE_PLAYING:
                    target_data, choice_data = generate_trial(STIMULI, current_rule)
                    target_card, choice_cards = build_cards(target_data, choice_data)
                    trial_start_time = pygame.time.get_ticks()

        if show_debug:
            rule_text = font.render(f"Rule: {current_rule}  Streak: {consecutive_correct}/{TRIALS_PER_RULE}", True, (0, 100, 255))
            screen.blit(rule_text, (50, 50))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()