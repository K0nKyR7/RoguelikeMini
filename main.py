import sys
import pygame as pg

CAPTION = "Echoes of the Forgotten Throne"

#Window size constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Game:
    
    def __init__(self):
        pg.init()
        
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption(CAPTION)
        
        self.player_x = WINDOW_WIDTH // 2
        self.player_y = WINDOW_HEIGHT // 2
        self.player_speed = 5
        
        self.running = True
        
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                    
    def handle_input(self):
        keys = pg.key.get_pressed()
        # WASD или стрелки
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.player_x -= self.player_speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.player_x += self.player_speed
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.player_y -= self.player_speed
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.player_y += self.player_speed
            
        self.player_x = max(0, min(self.player_x, WINDOW_WIDTH))
        self.player_y = max(0, min(self.player_y, WINDOW_HEIGHT))
    
    def draw(self):
        self.screen.fill(BLACK)
        
        #Player representation
        pg.draw.circle(self.screen, GREEN, 
                          (self.player_x, self.player_y), 10)
        
        font = pg.font.Font(None, 36)
        text = font.render("Movement: WASD / Arrows", 
                          True, WHITE)
        self.screen.blit(text, (10, 10))
        
        pg.display.flip()
    
    def run(self):
        #Game loop
        while self.running:
            self.handle_events()
            self.handle_input()
            self.draw()
        
        pg.quit()
        sys.exit()
        
if __name__ == "__main__":
    game = Game()
    game.run()