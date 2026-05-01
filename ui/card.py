import pygame

class Card:
    def __init__(
        self,
        text,
        semantic,     # e.g. "animals, tools etc."
        syntactic,    # e.g. "noun, adjective etc."
        syllables,    # e.g (1 or 2 count)
        rect
    ):
        self.text = text
        self.semantic = semantic
        self.syntactic = syntactic
        self.syllables = syllables
        self.rect = rect

    def draw(self, screen, font, hovered=False):
        # Fill with a light highlight when hovered, white otherwise
        fill_color = (220, 235, 255) if hovered else (255, 255, 255)
        pygame.draw.rect(screen, fill_color, self.rect, border_radius=8)

        # Border: thicker + blue tint when hovered
        border_color = (30, 100, 220) if hovered else (0, 0, 0)
        border_width = 3 if hovered else 2
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=8)

        label = font.render(self.text, True, (0, 0, 0))
        text_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

    # matching rule logic
    def matches_rule(self, other_card, rule):
        if rule == "semantic":
            return self.semantic == other_card.semantic

        elif rule == "syntactic":
            return self.syntactic == other_card.syntactic

        elif rule == "phonological":
            return self.syllables == other_card.syllables

        return False