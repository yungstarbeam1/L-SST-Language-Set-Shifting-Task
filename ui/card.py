import pygame

class Card:
    def __init__(self, text, semantic, syntactic, syllables, rect):
        self.text = text
        self.semantic = semantic
        self.syntactic = syntactic
        self.syllables = syllables
        self.rect = rect

    def is_clicked(self, mouse_pos):
        """Returns True if the mouse clicked within the card boundaries."""
        return self.rect.collidepoint(mouse_pos)

    def is_hovered(self, mouse_pos):
        """Returns True if the mouse is currently over the card."""
        return self.rect.collidepoint(mouse_pos)

    def matches_rule(self, target, rule):
        """
        Compares this card to the target card based on the active rule.
        Uses .lower() for strings and handles the 'phonological' vs 'syllables' naming.
        """
        # Normalize rule string to lowercase
        r = rule.lower()

        if r == "semantic":
            # Compare semantic category
            return str(self.semantic).lower() == str(target.semantic).lower()
        
        elif r == "syntactic":
            # Compare part of speech
            return str(self.syntactic).lower() == str(target.syntactic).lower()
        
        elif r == "syllables" or r == "phonological":
            # Handles the mismatch between the rule name and the data attribute
            try:
                return int(self.syllables) == int(target.syllables)
            except (ValueError, TypeError):
                # Fallback if data is non-numeric
                return self.syllables == target.syllables
                
        return False

    def draw(self, screen, font, theme, hovered=False):
        """
        Renders the card with theme-aware colors and hover effects.
        """
        # Background: Use theme's card color, slightly lightened if hovered
        base_color = theme["card_bg"]
        if hovered:
            # Create a subtle highlight effect
            fill_color = (min(base_color[0] + 20, 255), 
                          min(base_color[1] + 20, 255), 
                          min(base_color[2] + 25, 255))
        else:
            fill_color = base_color

        pygame.draw.rect(screen, fill_color, self.rect, border_radius=8)
        
        # Border logic: Blue highlight if hovered, otherwise standard gray
        border_color = (0, 120, 255) if hovered else (100, 100, 100)
        border_width = 3 if hovered else 2
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=8)

        # Text: Rendered using the theme's text color
        label = font.render(self.text, True, theme["text"])
        text_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, text_rect)