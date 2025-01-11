import pygame
import time

# Initialize Pygame
pygame.init()
w, h = 800, 800  # Outer frame (first screen)
w2, h2 = 770, 770  # Inner display (second screen)
screen = pygame.display.set_mode((w, h))  # First screen (frame)
screen2 = pygame.Surface((w2, h2))  # Second screen (content area)
fps = pygame.time.Clock()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 139)
YELLOW = (255, 255, 0)

# Load sounds
cdSound = pygame.mixer.Sound("assets//3sec_count.wav")
startSound = pygame.mixer.Sound("assets//start.wav")
endSound = pygame.mixer.Sound("assets//end.wav")
congratsSound = pygame.mixer.Sound("assets//congrats.wav")
tieSound = pygame.mixer.Sound("assets//tie.wav")

# Initialize scores and game state
team_a_score = 0
team_b_score = 0
prepare_time = 10
countdown_time = 15
extra_time = 5  # Extra time duration

# Game state variables
start_time = 0
starting = True
running = True
prepare_phase = True
in_extra_time = False
cdSoundplayed = False 
endSoundplayed = False
congratsSoundplayed = False
tieSoundplayed = False

def write(master, text_color, text, x, y, pos, size, outline_color=(0, 0, 0), outline_thickness=2):
    font = pygame.font.Font(None, size)

    # Render the text outline by blitting the text at multiple offsets
    def render_outline():
        for offset_x in range(-outline_thickness, outline_thickness + 1):
            for offset_y in range(-outline_thickness, outline_thickness + 1):
                if offset_x != 0 or offset_y != 0:  # Skip center to avoid overwriting
                    text_surface = font.render(str(text), True, outline_color)
                    master.blit(text_surface, (x + offset_x, y + offset_y))

    # Render the text in the middle or top-left as required
    if pos == "MIDDLE":
        width, height = font.size(text)
        x -= width / 2
        y -= height / 2

    # First draw the outline
    render_outline()

    # Draw the actual text on top of the outline
    text_surface = font.render(str(text), True, text_color)
    master.blit(text_surface, (x, y))


def reset_game():
    global team_a_score, team_b_score, starting, prepare_phase, start_time, in_extra_time
    team_a_score = 0
    team_b_score = 0
    starting = True
    prepare_phase = True
    start_time = 0
    in_extra_time = False

def display_result(winning_team, team_a_score=None, team_b_score=None):
    global congratsSoundplayed, tieSoundplayed
    
    congratsSoundplayed = False
    tieSoundplayed = False
    
    # Show result 
    for _ in range(60):  # Approximate 1 second at 60 FPS
        screen.fill(WHITE)  # Frame background color
        screen2.fill(BLACK)  # Main content background
        
        if winning_team == "Team A WIN":
            write(screen2, RED, winning_team, w2 / 2, h2 / 2, "MIDDLE", 70)
            write(screen2, RED, f"Score: {team_a_score}", w2 / 2, h2 / 2 + 50, "MIDDLE", 60)
            if not congratsSoundplayed:
                congratsSound.play()
                congratsSoundplayed = True
        elif winning_team == "Team B WIN":
            write(screen2, BLUE, winning_team, w2 / 2, h2 / 2, "MIDDLE", 70)
            write(screen2, BLUE, f"Score: {team_b_score}", w2 / 2, h2 / 2 + 50, "MIDDLE", 60)
            if not congratsSoundplayed:
                congratsSound.play()
                congratsSoundplayed = True
        else:
            write(screen2, BLACK, winning_team, w2 / 2, h2 / 2, "MIDDLE", 70)
            write(screen2, BLACK, f"Team A: {team_a_score}, Team B: {team_b_score}", w2 / 2, h2 / 2 + 50, "MIDDLE", 60)
            if not tieSoundplayed:
                tieSound.play()
                tieSoundplayed = True
        
        # Blit second screen onto the first screen (centered)
        screen.blit(screen2, ((w - w2) / 2, (h - h2) / 2))
        pygame.display.flip()
        fps.tick(60)

def loop():
    global running, starting, prepare_phase, start_time
    global team_a_score, team_b_score
    global cdSoundplayed, endSoundplayed, congratsSoundplayed, tieSoundplayed
    global in_extra_time  

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and starting:
                    start_time = time.time()
                    starting = False
                    startSound.play()

                # Team A scoring
                if event.key == pygame.K_7:
                    team_a_score += 7
                if event.key == pygame.K_3:
                    team_a_score += 3
                if event.key == pygame.K_2:
                    team_a_score += 2

                # Team B scoring
                if event.key == pygame.K_KP7:
                    team_b_score += 7
                if event.key == pygame.K_KP3:
                    team_b_score += 3
                if event.key == pygame.K_KP2:
                    team_b_score += 2

                # Press R to reset the game
                if event.key == pygame.K_r:
                    reset_game()

        # Initialize timer variables
        minutes = 0
        seconds = 0
        remaining_prepare_time = prepare_time

        if not starting:
            time_elapsed = time.time() - start_time

            if prepare_phase:
                remaining_prepare_time = prepare_time - int(time_elapsed)

                if remaining_prepare_time <= 3 and not cdSoundplayed:
                    cdSound.play()
                    cdSoundplayed = True

                if remaining_prepare_time <= 0:
                    prepare_phase = False
                    start_time = time.time()

            else:
                # Main countdown phase
                remaining_time = countdown_time - int(time_elapsed)

                if remaining_time <= 0:
                    if team_a_score == team_b_score:
                        in_extra_time = True
                        start_time = time.time()
                    else:
                        # Determine winner without extra time
                        if team_a_score > team_b_score:
                            display_result("Team A WIN", team_a_score=team_a_score)
                        elif team_b_score > team_a_score:
                            display_result("Team B WIN", team_b_score=team_b_score)
                        else:
                            display_result("It's a Tie!", team_a_score=team_a_score, team_b_score=team_b_score)

                        reset_game()  # Reset game after showing result
                        continue

                if in_extra_time:
                    remaining_time = extra_time - int(time.time() - start_time)
                    if remaining_time <= 0:
                        # Determine winner
                        if team_a_score > team_b_score:
                            display_result("Team A WIN", team_a_score=team_a_score)
                        elif team_b_score > team_a_score:
                            display_result("Team B WIN", team_b_score=team_b_score)
                        else:
                            display_result("It's a Tie!", team_a_score=team_a_score, team_b_score=team_b_score)
                                                
                        reset_game()  # Reset game after showing result
                        continue

                # Convert remaining time into minutes and seconds
                minutes = remaining_time // 60
                seconds = remaining_time % 60

        # Fill the first screen with a frame background color
        screen.fill(WHITE)
        screen2.fill(BLACK)  # Second screen content

        # Display the title on the second screen
        write(screen2, WHITE, "DCLabs Robocon", w2 / 2, h2 / 10, "MIDDLE", 70)

        if starting:
            write(screen2, WHITE, "Press SPACE to Start", w2 / 2, h2 / 7 + 40, "MIDDLE", 50)
        elif prepare_phase:
            write(screen2, WHITE, f"Prepare: {remaining_prepare_time}s", w2 / 2, 150, "MIDDLE", 60)
        else:
            if in_extra_time:
                write(screen2, WHITE, f"Extra Time: {remaining_time}s", w2 / 2, 150, "MIDDLE", 60)
            else:
                write(screen2, WHITE, f"Time: {minutes:02}:{seconds:02}", w2 / 2, 150, "MIDDLE", 60)


        # Display Team labels (A and B) with outlines
        write(screen2, RED, "Team A", w2 / 4, 250, "MIDDLE", 60, outline_color=WHITE, outline_thickness=2)
        write(screen2, YELLOW, f"{team_a_score}", w2 / 4, 300, "MIDDLE", 60)
        write(screen2, BLUE, "Team B", 3 * w2 / 4, 250, "MIDDLE", 60, outline_color=WHITE, outline_thickness=2)
        write(screen2, YELLOW, f"{team_b_score}", 3 * w2 / 4, 300, "MIDDLE", 60)
 
        # Blit the second screen onto the first screen (centered)
        screen.blit(screen2, ((w - w2) / 2, (h - h2) / 2))
        pygame.display.flip()
        fps.tick(60)

# Start the game loop
loop()
pygame.quit()