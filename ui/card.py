import pygame

class Card:
    def __init__(self, text, semantic, length, syllables, rect):
        self.text      = text
        self.semantic  = semantic
        self.length    = length     # "short" / "medium" / "long"
        self.syllables = syllables
        self.rect      = rect

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def matches_rule(self, target, rule):
        r = rule.lower()

        if r == "semantic":
            return str(self.semantic).lower() == str(target.semantic).lower()

        elif r == "length":
            return str(self.length).lower() == str(target.length).lower()

        elif r in ("syllables", "phonological"):
            try:
                return int(self.syllables) == int(target.syllables)
            except (ValueError, TypeError):
                return self.syllables == target.syllables

        return False

    def draw(self, screen, font, theme, hovered=False):
        base_color = theme["card_bg"]
        if hovered:
            fill_color = (
                min(base_color[0] + 20, 255),
                min(base_color[1] + 20, 255),
                min(base_color[2] + 25, 255),
            )
        else:
            fill_color = base_color

        pygame.draw.rect(screen, fill_color, self.rect, border_radius=8)

        border_color = (0, 120, 255) if hovered else (100, 100, 100)
        border_width = 3 if hovered else 2
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=8)

        label = font.render(self.text, True, theme["text"])
        screen.blit(label, label.get_rect(center=self.rect.center))