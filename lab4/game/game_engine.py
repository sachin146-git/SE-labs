import pygame
import random
from .hole import Hole

# Game Engine

DARK_BROWN = (60, 40, 20)
MOLE_BROWN = (140, 95, 55)
BLACK = (0, 0, 0)


class GameEngine:
    def __init__(self, width, height, rows=3, cols=3):
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols

        self.font = pygame.font.SysFont("Arial", 28)

        # Sound effects
        pygame.mixer.init()
        self.whack_sound = pygame.mixer.Sound("assets/sounds/whack.wav")
        self.miss_sound = pygame.mixer.Sound("assets/sounds/miss.wav")
        self.game_over_sound = pygame.mixer.Sound(
            "assets/sounds/game_over.wav"
        )

        # Default difficulty
        self.difficulty = "Medium"

        self._setup_game()

    def _setup_game(self):
        self.holes = []

        spacing_x = self.width // (self.cols + 1)
        spacing_y = (self.height - 80) // (self.rows + 1)

        for r in range(self.rows):
            for c in range(self.cols):
                cx = spacing_x * (c + 1)
                cy = 80 + spacing_y * (r + 1)
                self.holes.append(Hole(cx, cy))

        # Difficulty settings:
        # Easy   -> fewer moles, stay up longer
        # Medium -> default
        # Hard   -> more moles, stay up for less time
        difficulty_settings = {
            "Easy": (0.015, 60),
            "Medium": (0.02, 45),
            "Hard": (0.03, 30)
        }

        self.spawn_chance, self.mole_up_frames = (
            difficulty_settings[self.difficulty]
        )

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.score = 0
        self.misses = 0
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        # Game Over input is handled separately
        if self.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_game_over_click(event.pos)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        hit_something = False

        for hole in self.holes:
            if hole.rect().collidepoint(pos):
                if hole.whack():
                    self.score += 1
                    hit_something = True

                    # Successful whack sound
                    self.whack_sound.play()

                    # IMPORTANT:
                    # One click can only hit one mole.
                    break

        if not hit_something:
            self.misses += 1

            # Miss sound
            self.miss_sound.play()

    def _handle_game_over_click(self, pos):
        button_width = 200
        button_height = 45
        center_x = self.width // 2

        buttons = {
            "Easy": pygame.Rect(
                center_x - button_width // 2,
                300,
                button_width,
                button_height
            ),
            "Medium": pygame.Rect(
                center_x - button_width // 2,
                355,
                button_width,
                button_height
            ),
            "Hard": pygame.Rect(
                center_x - button_width // 2,
                410,
                button_width,
                button_height
            ),
            "Exit": pygame.Rect(
                center_x - button_width // 2,
                465,
                button_width,
                button_height
            )
        }

        for difficulty, rect in buttons.items():
            if rect.collidepoint(pos):
                if difficulty == "Exit":
                    pygame.quit()
                    raise SystemExit

                self.difficulty = difficulty
                self._setup_game()
                return

    def handle_input(self):
        # Reserved for continuously-held-key input.
        # This game is entirely mouse-driven.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1

        if self.time_left_frames <= 0:
            self.game_over = True

            # Play once when the round ends
            self.game_over_sound.play()

            return

        for hole in self.holes:
            hole.update()

            if not hole.active and random.random() < self.spawn_chance:
                hole.pop_up(self.mole_up_frames)

    def render(self, screen):
        # Draw holes and moles
        for hole in self.holes:
            pygame.draw.circle(
                screen,
                DARK_BROWN,
                (hole.center_x, hole.center_y),
                40
            )

            if hole.active:
                pygame.draw.circle(
                    screen,
                    MOLE_BROWN,
                    (hole.center_x, hole.center_y),
                    32
                )

        # Score
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            BLACK
        )
        screen.blit(score_text, (10, 10))

        # Timer
        seconds_left = max(
            0,
            self.time_left_frames // 60
        )

        timer_text = self.font.render(
            f"Time: {seconds_left}s",
            True,
            BLACK
        )

        screen.blit(
            timer_text,
            (self.width - 140, 10)
        )

        # Game Over screen
        if self.game_over:
            game_over_text = self.font.render(
                "GAME OVER",
                True,
                BLACK
            )

            final_score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                BLACK
            )

            choose_text = self.font.render(
                "Choose Difficulty",
                True,
                BLACK
            )

            screen.blit(
                game_over_text,
                game_over_text.get_rect(
                    center=(self.width // 2, 130)
                )
            )

            screen.blit(
                final_score_text,
                final_score_text.get_rect(
                    center=(self.width // 2, 175)
                )
            )

            screen.blit(
                choose_text,
                choose_text.get_rect(
                    center=(self.width // 2, 240)
                )
            )

            self._render_menu_buttons(screen)

    def _render_menu_buttons(self, screen):
        button_width = 200
        button_height = 45
        center_x = self.width // 2

        buttons = [
            ("Easy", 300),
            ("Medium", 355),
            ("Hard", 410),
            ("Exit", 465)
        ]

        for text, y in buttons:
            rect = pygame.Rect(
                center_x - button_width // 2,
                y,
                button_width,
                button_height
            )

            pygame.draw.rect(
                screen,
                DARK_BROWN,
                rect
            )

            button_text = self.font.render(
                text,
                True,
                (255, 255, 255)
            )

            screen.blit(
                button_text,
                button_text.get_rect(
                    center=rect.center
                )
            )