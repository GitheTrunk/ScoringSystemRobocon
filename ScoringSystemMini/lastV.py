import pygame

# Initialize Pygame
pygame.init()

# Constants for screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800 * 2 - 30, 800  # Outer frame
INNER_WIDTH, INNER_HEIGHT = 770 * 2 - 30, 770  # Inner display
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Load sounds with error handling
def load_sounds():
    sound_files = {
        "cd": "assets/3sec_count.wav",
        "start": "assets/start.wav",
        "end": "assets/end.wav",
        "congrats": "assets/congrats.wav",
        "tie": "assets/tie.wav",
    }
    sounds = {}
    for key, path in sound_files.items():
        try:
            sounds[key] = pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"Failed to load sound {key}: {e}")
    return sounds

# Initialize game variables
team_a_score = 0
team_b_score = 0
prepare_time = 8
countdown_time = 60
extra_time = 10

# Initialize shot clock variables
team_a_shot_time = 10  
team_b_shot_time = 10
current_shot_time = team_a_shot_time  
active_team = "A"  
shot_clock_start_time = 0  

# Game state variables
start_time = 0
starting = True
running = True
prepare_phase = True
in_extra_time = False

# Load sounds
sounds = load_sounds()

# Create display surfaces
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen2 = pygame.Surface((INNER_WIDTH, INNER_HEIGHT))
fps = pygame.time.Clock()

def draw_text(surface, color, text, x, y, pos, size, outline_color=(0, 0, 0), outline_thickness=2):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if pos == "MIDDLE":
        x -= text_rect.width / 2
        y -= text_rect.height / 2

    # Draw the outline
    for offset_x in range(-outline_thickness, outline_thickness + 1):
        for offset_y in range(-outline_thickness, outline_thickness + 1):
            if offset_x != 0 or offset_y != 0:
                outline_surface = font.render(text, True, outline_color)
                surface.blit(outline_surface, (x + offset_x, y + offset_y))

    surface.blit(text_surface, (x, y))

def reset_shot_clock():
    global active_team, current_shot_time, shot_clock_start_time
    current_shot_time = team_b_shot_time if active_team == "A" else team_a_shot_time
    active_team = "B" if active_team == "A" else "A"
    shot_clock_start_time = pygame.time.get_ticks()  # Restart shot clock timer

def reset_game():
    global team_a_score, team_b_score, starting, prepare_phase, start_time, in_extra_time
    team_a_score = 0
    team_b_score = 0
    starting = True
    prepare_phase = True
    start_time = 0
    in_extra_time = False

def display_result(winning_team):
    for _ in range(60):  # Approximate 1 second at 60 FPS
        screen.fill(WHITE)
        screen2.fill(BLACK)

        if winning_team == "Team A WIN":
            draw_text(screen2, RED, winning_team, INNER_WIDTH / 2, INNER_HEIGHT / 2, "MIDDLE", 100, outline_color=WHITE)
            draw_text(screen2, RED, f"Score: {team_a_score}", INNER_WIDTH / 2, INNER_HEIGHT / 2 + 100, "MIDDLE", 90)
            sounds["congrats"].play()
        elif winning_team == "Team B WIN":
            draw_text(screen2, BLUE, winning_team, INNER_WIDTH / 2, INNER_HEIGHT / 2, "MIDDLE", 100, outline_color=WHITE)
            draw_text(screen2, BLUE, f"Score: {team_b_score}", INNER_WIDTH / 2, INNER_HEIGHT / 2 + 100, "MIDDLE", 100, outline_color=WHITE)
            sounds["congrats"].play()
        else:
            draw_text(screen2, BLACK, winning_team, INNER_WIDTH / 2, INNER_HEIGHT / 2, "MIDDLE", 100, outline_color=WHITE)
            draw_text(screen2, BLACK, f"Team A: {team_a_score} | Team B: {team_b_score}", 
                      INNER_WIDTH / 2, INNER_HEIGHT / 2 + 100, "MIDDLE", 90, outline_color=WHITE)
            sounds["tie"].play()

        screen.blit(screen2, ((SCREEN_WIDTH - INNER_WIDTH) / 2, (SCREEN_HEIGHT - INNER_HEIGHT) / 2))
        pygame.display.flip()
        fps.tick(FPS)


def update_shot_clock():
    elapsed_shot_time = (pygame.time.get_ticks() - shot_clock_start_time) / 1000  # Convert to seconds
    remaining_shot_time = current_shot_time - elapsed_shot_time
    
    if remaining_shot_time <= 0: 
        # When the shot clock ends, switch the active team
        reset_shot_clock()
        remaining_shot_time = current_shot_time  # Reset to the shot time for the next team
    
    return remaining_shot_time

def game_loop():
    global running, starting, prepare_phase, start_time, team_a_score, team_b_score, shot_clock_start_time
    global in_extra_time

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and starting:
                    start_time = pygame.time.get_ticks()
                    starting = False
                    sounds["start"].play()

                # Team A scoring
                if active_team == "A" and event.key in (pygame.K_7, pygame.K_3, pygame.K_2):
                    points = {pygame.K_7: 7, pygame.K_3: 3, pygame.K_2: 2}
                    team_a_score += points[event.key]
                    # Do not reset shot clock here; allow multiple scores within the shot clock time

                # Team B scoring
                if active_team == "B" and event.key in (pygame.K_KP7, pygame.K_KP3, pygame.K_KP2):
                    points = {pygame.K_KP7: 7, pygame.K_KP3: 3, pygame.K_KP2: 2}
                    team_b_score += points[event.key]
                    # Do not reset shot clock here; allow multiple scores within the shot clock time

                # Reset game
                if event.key == pygame.K_r:
                    reset_game()

        # Initialize timer variables
        minutes = 0
        seconds = 0
        remaining_prepare_time = prepare_time

        if not starting:
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Convert to seconds

            if prepare_phase:
                remaining_prepare_time = prepare_time - int(elapsed_time)
                if remaining_prepare_time <= 3:
                    sounds["cd"].play()
                if remaining_prepare_time <= 0:
                    prepare_phase = False
                    start_time = pygame.time.get_ticks()  # Reset the start time
                    shot_clock_start_time = pygame.time.get_ticks()
            else:
                # Main countdown phase
                remaining_time = countdown_time - int(elapsed_time)

                if remaining_time <= 0:
                    if team_a_score == team_b_score:
                        in_extra_time = True
                        start_time = pygame.time.get_ticks()
                    else:
                        winner = "Team A WIN" if team_a_score > team_b_score else "Team B WIN"
                        display_result(winner)
                        reset_game()  # Reset game after showing result
                        continue

                if in_extra_time:
                    remaining_time = extra_time - int((pygame.time.get_ticks() - start_time) / 1000)  # Convert to seconds
                    if remaining_time <= 0:
                        if team_a_score > team_b_score:
                            winner = "Team A WIN" 
                        elif team_b_score > team_a_score:
                            winner = "Team B WIN"
                        else:
                            winner = "It's Tie"
                    
                        display_result(winner)
                        reset_game()  # Reset game after showing result
                        continue

                # Convert remaining time into minutes and seconds
                minutes = remaining_time // 60
                seconds = remaining_time % 60

        # Fill screens
        screen.fill(WHITE)
        screen2.fill(BLACK)

        # Display title
        draw_text(screen2, WHITE, "DCLabs Robocon", INNER_WIDTH / 2, INNER_HEIGHT / 10, "MIDDLE", 50)

        if starting:
            draw_text(screen2, WHITE, "Press SPACE to Start", INNER_WIDTH / 2, INNER_HEIGHT / 7 + 40, "MIDDLE", 50)
        elif prepare_phase:
            draw_text(screen2, WHITE, f"Prepare: {remaining_prepare_time}s", INNER_WIDTH / 2, 150, "MIDDLE", 60)
        else:
            remaining_shot_time = update_shot_clock()
            time_display = f"Extra Time: {remaining_time}s" if in_extra_time else f"Time: {minutes:02}:{seconds:02}"
            draw_text(screen2, WHITE, time_display, INNER_WIDTH / 2, 150, "MIDDLE", 60)

            if active_team == "A":
                draw_text(screen2, RED, f"Shot Clock: {remaining_shot_time:.1f}s", INNER_WIDTH / 6 - 10, 225, "MIDDLE", 60, outline_color=WHITE)
            else:
                draw_text(screen2, BLUE, f"Shot Clock: {remaining_shot_time:.1f}s", 4 * INNER_WIDTH / 6 - 10, 225, "MIDDLE", 60, outline_color=WHITE)
                
        # Display team scores
        draw_text(screen2, RED, "Team A", INNER_WIDTH / 4, 350, "MIDDLE", 90, outline_color=WHITE)
        draw_text(screen2, YELLOW, str(team_a_score), INNER_WIDTH / 4, 450, "MIDDLE", 120)

        draw_text(screen2, BLUE, "Team B", 3 * INNER_WIDTH / 4, 350, "MIDDLE", 90, outline_color=WHITE)
        draw_text(screen2, YELLOW, str(team_b_score), 3 * INNER_WIDTH / 4, 450, "MIDDLE", 120)

        screen.blit(screen2, ((SCREEN_WIDTH - INNER_WIDTH) / 2, (SCREEN_HEIGHT - INNER_HEIGHT) / 2))
        pygame.display.flip()
        fps.tick(FPS)

# Start the game loop
game_loop()
pygame.quit()