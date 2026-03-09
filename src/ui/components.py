import pygame

class FleetUI:
    def draw_unit_card(self, screen, data, pos):
        # Parchment background
        rect = pygame.Rect(pos[0], pos[1], 250, 300)
        pygame.draw.rect(screen, (240, 230, 200), rect)
        
        # Stats rendering
        font = pygame.font.SysFont("Georgia", 20)
        title = font.render(f"{data['name']}", True, (0,0,0))
        screen.blit(title, (pos[0]+10, pos[1]+10))
        
        # Trait logic display
        y = 50
        for trait in data['traits']:
            t_surface = font.render(f"• {trait.upper()}", True, (150, 0, 0))
            screen.blit(t_surface, (pos[0]+10, pos[1]+y))
            y += 30