import pygame
import random

from ui.card import Card
from engine.stimuli import STIMULI
from engine.trial_generator import generate_trial
from engine.lsst_logic import LSSTEngine
from settings import RULES, TRIALS_PER_RULE

pygame.init()

# FULLSCREEN SETUP
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("LS-ST")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)

CURSOR_HAND  = pygame.SYSTEM_CURSOR_HAND
CURSOR_ARROW = pygame.SYSTEM_CURSOR_ARROW

engine = LSSTEngine()

#  WCST-STYLE RULE STATE 
rule_order = RULES[:]          
rule_index = 0                 
current_rule = rule_order[rule_index]
consecutive_correct = 0        
trial_number = 0               

# FEEDBACK & RESULTS STATE
feedback = None
feedback_time = 0
show_feedback = False
show_results = False # New state for game over[cite: 1]

# DEBUG HUD
show_debug = False

# TIMING
trial_start_time = pygame.time.get_ticks()

#  CARD BUILDER 
def build_cards(target_data, choice_data):
    target_rect = pygame.Rect((WIDTH - 200) // 2, (HEIGHT - 100) // 2 - 200, 200, 100)
    target = Card(
        target_data["text"],
        target_data["semantic"],
        target_data["syntactic"],
        target_data["syllables"],
        target_rect
    )

    x_positions = [WIDTH // 2 - 300, WIDTH // 2 - 100, WIDTH // 2 + 100]
    choices = []
    for i, c in enumerate(choice_data):
        rect = pygame.Rect(x_positions[i], HEIGHT - 200, 180, 100)
        choices.append(Card(
            c["text"], c["semantic"], c["syntactic"], c["syllables"], rect
        ))
    return target, choices

#   FEEDBACK DRAW 
def draw_feedback(surface, w, h, state):
    # Dim background[cite: 1]
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 180))
    surface.blit(overlay, (0, 0))

    cx, cy = w // 2, h // 2
    radius = 60
    COLOR_CORRECT = (46, 204, 113)
    COLOR_WRONG   = (231, 76, 60)

    if state == "correct":
        pygame.draw.circle(surface, COLOR_CORRECT, (cx, cy), radius)
        points = [(cx - 25, cy), (cx - 5, cy + 20), (cx + 30, cy - 20)]
        pygame.draw.lines(surface, (255, 255, 255), False, points, 10)
    else:
        pygame.draw.circle(surface, COLOR_WRONG, (cx, cy), radius)
        offset = 20
        pygame.draw.line(surface, (255, 255, 255), (cx-offset, cy-offset), (cx+offset, cy+offset), 10)
        pygame.draw.line(surface, (255, 255, 255), (cx+offset, cy-offset), (cx-offset, cy+offset), 10)

# RESULTS SCREEN
def draw_results_screen(surface, w, h, total_trials):
    surface.fill((240, 245, 250))
    title_font = pygame.font.Font(None, 80)
    res_font = pygame.font.Font(None, 50)
    
    title_surf = title_font.render("TASK COMPLETE", True, (44, 62, 80))
    surface.blit(title_surf, title_surf.get_rect(center=(w // 2, h // 2 - 100)))

    trials_surf = res_font.render(f"Total Trials: {total_trials}", True, (52, 73, 94))
    surface.blit(trials_surf, trials_surf.get_rect(center=(w // 2, h // 2)))

    exit_surf = res_font.render("Press ESC to exit", True, (127, 140, 141))
    surface.blit(exit_surf, exit_surf.get_rect(center=(w // 2, h // 2 + 100)))

# INITIAL TRIAL
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

        if not show_results and not show_feedback:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for card in choice_cards:
                    if card.is_clicked(mouse_pos):
                        correct = engine.check(target_card, card, current_rule)
                        rt = pygame.time.get_ticks() - trial_start_time
                        trial_number += 1
                        
                        if correct:
                            consecutive_correct += 1
                        else:
                            consecutive_correct = 0   

                        feedback = "correct" if correct else "incorrect"
                        show_feedback = True
                        feedback_time = pygame.time.get_ticks()

# INTERACT LOGIC 
    if show_results:
        draw_results_screen(screen, WIDTH, HEIGHT, trial_number)
        pygame.mouse.set_cursor(CURSOR_ARROW) # Ensure arrow on results screen
    else:
        screen.fill((255, 255, 255))
        
        # Update cursor state based on hover
        any_hovered = (not show_feedback) and any(c.is_hovered(mouse_pos) for c in choice_cards)
        pygame.mouse.set_cursor(CURSOR_HAND if any_hovered else CURSOR_ARROW)
               
        # TARGET
        label = font.render("TARGET", True, (0, 0, 0))
        screen.blit(label, label.get_rect(center=(target_card.rect.centerx, target_card.rect.top - 40)))
        target_card.draw(screen, font)

        # CHOICES
        for card in choice_cards:
            # Cards only highlight if we aren't currently showing feedback[cite: 1]
            hovered = (not show_feedback) and card.is_hovered(mouse_pos)
            card.draw(screen, font, hovered=hovered)

        if show_feedback:
            draw_feedback(screen, WIDTH, HEIGHT, feedback)
            if pygame.time.get_ticks() - feedback_time > 600:
                show_feedback = False
                
                # Rule transition logic[cite: 1, 2]
                if consecutive_correct >= TRIALS_PER_RULE:
                    consecutive_correct = 0
                    rule_index += 1
                    if rule_index >= len(rule_order):
                        show_results = True[cite: 1]
                    else:
                        current_rule = rule_order[rule_index]

                # Generate next trial only if the task isn't over
                if not show_results:
                    target_data, choice_data = generate_trial(STIMULI, current_rule)
                    target_card, choice_cards = build_cards(target_data, choice_data)
                    trial_start_time = pygame.time.get_ticks()

        if show_debug:
            rule_text = font.render(f"Rule: {current_rule}  Streak: {consecutive_correct}/{TRIALS_PER_RULE}", True, (0, 0, 200))
            screen.blit(rule_text, (50, 50))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()