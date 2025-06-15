import math
import pygame

def draw_dashboard(self):
    """Renders the car's dashboard."""

    screen = self.main.screen

    # Base panel
    dash_rect = pygame.Rect(20, screen.get_height() - 180, 300, 160)
    pygame.draw.rect(screen, (20, 20, 20), dash_rect, border_radius=10)
    pygame.draw.rect(screen, (80, 80, 80), dash_rect, 3, border_radius=10)

    center_x = dash_rect.x + 80
    center_y = dash_rect.y + 80

    # === Fuel Gauge ===
    pygame.draw.circle(screen, (0, 0, 0), (center_x - 40, center_y), 30)
    pygame.draw.circle(screen, (200, 200, 200), (center_x - 40, center_y), 30, 2)

    # Fuel arc (from top-left to bottom-left)
    for i in range(0, 181, 5):
        angle = math.radians(135 + i)
        fx = center_x - 40 + 28 * math.cos(angle)
        fy = center_y + 28 * math.sin(angle)
        pygame.draw.circle(screen, (60, 60, 60), (int(fx), int(fy)), 1)

    # Fuel needle
    fuel_percent = 0.6  # You can connect this to self.car.fuel / self.car.max_fuel
    fuel_angle = math.radians(135 + (fuel_percent * 180))
    fx = center_x - 40 + 25 * math.cos(fuel_angle)
    fy = center_y + 25 * math.sin(fuel_angle)
    pygame.draw.line(screen, (255, 0, 0), (center_x - 40, center_y), (fx, fy), 3)

    self._draw_text("E", center_x - 40 - 6, center_y - 28, (255, 255, 255), size=20)
    self._draw_text("F", center_x - 40 - 6, center_y + 20, (255, 255, 255), size=20)

    # === Speedometer ===
    pygame.draw.circle(screen, (0, 0, 0), (center_x + 60, center_y), 40)
    pygame.draw.circle(screen, (200, 200, 200), (center_x + 60, center_y), 40, 2)

    speed_value = max(0, min(abs(self.car.speed) * 10, 60))
    speed_angle = math.radians(135 - (speed_value / 60) * 180)
    sx = center_x + 60 + 30 * math.cos(speed_angle)
    sy = center_y + 30 * math.sin(speed_angle)
    pygame.draw.line(screen, (255, 255, 255), (center_x + 60, center_y), (sx, sy), 3)

    # Speedometer labels (0, 20, 40, 60)
    for val in range(0, 61, 20):
        label_angle = math.radians(135 - (val / 60) * 180)
        lx = center_x + 60 + 38 * math.cos(label_angle)
        ly = center_y + 38 * math.sin(label_angle)
        self._draw_text(str(val), lx - 10, ly - 10, (255, 255, 255), size=16)

    # === Brake Indicator ===
    if self.brake_pressed:
        pygame.draw.rect(screen, (200, 0, 0), (dash_rect.x + 10, dash_rect.bottom - 40, 80, 30))
        self._draw_text("BRAKE", dash_rect.x + 15, dash_rect.bottom - 37, (0, 0, 0), size=24)

    # === Handbrake Indicator ===
    if self.car.is_handbraking():
        pygame.draw.circle(screen, (200, 0, 0), (dash_rect.right - 30, dash_rect.bottom - 30), 15)
        self._draw_text("P", dash_rect.right - 36, dash_rect.bottom - 38, (0, 0, 0), size=24)
