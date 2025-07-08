import pygame
import pymunk
import math

# --- Constants ---
WIDTH, HEIGHT = 1000, 600  # Increased width to include sidebar
BALL_RADIUS = 15
WALL_THICKNESS = 10
BLUE = (0, 0, 255)
RED = (255, 0, 0)
SIDEBAR_WIDTH = 200
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 40
GRAVITY_STEP = 100

pygame.init()
FONT = pygame.font.SysFont("Arial", 20)

class PhysicsSimulation:
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Physics Simulation")
        self.clock = pygame.time.Clock()
        self.space = pymunk.Space()
        self.gravity_y = 900
        self.space.gravity = (0, self.gravity_y)
        self.balls = []
        self.dragging_ball = None
        self.drag_offset = (0, 0)
        self.ball_colors = {}
        self.create_walls()

    def create_walls(self):
        static_lines = [
            pymunk.Segment(self.space.static_body, (0, 0), (0, HEIGHT), WALL_THICKNESS),
            pymunk.Segment(self.space.static_body, (0, HEIGHT), (WIDTH - SIDEBAR_WIDTH, HEIGHT), WALL_THICKNESS),
            pymunk.Segment(self.space.static_body, (WIDTH - SIDEBAR_WIDTH, HEIGHT), (WIDTH - SIDEBAR_WIDTH, 0), WALL_THICKNESS),
            pymunk.Segment(self.space.static_body, (WIDTH - SIDEBAR_WIDTH, 0), (0, 0), WALL_THICKNESS),
        ]
        for line in static_lines:
            line.elasticity = 0.95
            line.friction = 0.9
        self.space.add(*static_lines)

    def is_valid_position(self, pos):
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            return False
        x, y = pos
        return (
            0 < x < WIDTH - SIDEBAR_WIDTH and
            0 < y < HEIGHT and
            not math.isnan(x) and
            not math.isnan(y) and
            not math.isinf(x) and
            not math.isinf(y)
        )

    def create_ball(self, pos):
        if not self.is_valid_position(pos):
            return

        mass = 1
        inertia = pymunk.moment_for_circle(mass, 0, BALL_RADIUS)
        body = pymunk.Body(mass, inertia)
        body.position = pos
        shape = pymunk.Circle(body, BALL_RADIUS)
        shape.elasticity = 0.95
        shape.friction = 0.9
        self.space.add(body, shape)
        self.balls.append(shape)
        self.ball_colors[shape] = BLUE

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Sidebar button handling
                if self.increase_button.collidepoint(mouse_pos):
                    self.gravity_y += GRAVITY_STEP
                elif self.decrease_button.collidepoint(mouse_pos):
                    self.gravity_y = max(0, self.gravity_y - GRAVITY_STEP)
                else:
                    for ball in self.balls:
                        if pymunk.Vec2d(*mouse_pos).get_distance(ball.body.position) < BALL_RADIUS:
                            self.dragging_ball = ball
                            self.drag_offset = ball.body.position - pymunk.Vec2d(*mouse_pos)
                            ball.body.velocity = (0, 0)
                            ball.body.angular_velocity = 0
                            break
                    else:
                        self.create_ball(mouse_pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_ball = None

        return True

    def update_drag(self):
        if self.dragging_ball:
            mouse_pos = pygame.mouse.get_pos()
            new_pos = pymunk.Vec2d(*mouse_pos) + self.drag_offset
            self.dragging_ball.body.position = new_pos
            self.dragging_ball.body.velocity = (0, 0)
            self.dragging_ball.body.angular_velocity = 0

    def draw_balls(self):
        for ball in self.balls:
            pos = ball.body.position
            if any([
                math.isnan(pos.x), math.isnan(pos.y),
                math.isinf(pos.x), math.isinf(pos.y)
            ]):
                continue

            pygame.draw.circle(self.window, self.ball_colors.get(ball, BLUE), (int(pos.x), int(pos.y)), BALL_RADIUS)
            if ball == self.dragging_ball:
                pygame.draw.circle(self.window, RED, (int(pos.x), int(pos.y)), BALL_RADIUS + 2, 2)

    def draw_sidebar(self):
        sidebar_x = WIDTH - SIDEBAR_WIDTH
        pygame.draw.rect(self.window, (240, 240, 240), (sidebar_x, 0, SIDEBAR_WIDTH, HEIGHT))

        # Increase Gravity Button
        self.increase_button = pygame.Rect(sidebar_x + 20, 50, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.window, (200, 200, 255), self.increase_button)
        self.window.blit(FONT.render("↑ Increase", True, (0, 0, 0)), (sidebar_x + 50, 60))

        # Decrease Gravity Button
        self.decrease_button = pygame.Rect(sidebar_x + 20, 110, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.window, (255, 200, 200), self.decrease_button)
        self.window.blit(FONT.render("↓ Decrease", True, (0, 0, 0)), (sidebar_x + 50, 120))

        # Current Gravity Display
        gravity_label = FONT.render("Gravity Y:", True, (0, 0, 0))
        gravity_value = FONT.render(f"{self.gravity_y}", True, (0, 0, 0))
        self.window.blit(gravity_label, (sidebar_x + 20, 180))
        self.window.blit(gravity_value, (sidebar_x + 20, 210))

    def run(self):
        running = True
        while running:
            self.window.fill((255, 255, 255))
            running = self.handle_events()
            self.update_drag()
            self.space.gravity = (0, self.gravity_y)
            self.space.step(1 / 60.0)
            self.draw_balls()
            self.draw_sidebar()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == '__main__':
    PhysicsSimulation().run()
