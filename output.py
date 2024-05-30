import direction
import ball

from colorama import init, Fore, Style, Back
import os

init()


TRAIL_LEN = 3
BORDER_NW = "╭"
BORDER_SW = "╰"
BORDER_NE = "╮"
BORDER_SE = "╯"
BORDER_HZ = "─"
BORDER_VT = "│"
BALL_CHAR = "•"
BALL_SHADOW = "."
BLANK_SPACE = " "
COLLISION_CHAR = f"{Style.RESET_ALL}{Back.RED}{Fore.YELLOW}!{Back.RESET}{Fore.RESET}"
BALLS_COLORS = [
    Fore.RED,
    Fore.BLUE,
    Fore.WHITE,
    Fore.YELLOW,
    Fore.GREEN,
    Fore.MAGENTA,
    Fore.CYAN
]

border_width = None
border_height = None
_ball_color_index = -1

def wrapping_get_ball_color():
    global _ball_color_index
    _ball_color_index += 1
    if _ball_color_index > len(BALLS_COLORS) - 1:
        _ball_color_index = 0

    return BALLS_COLORS[_ball_color_index]

def is_ball_at_position(x: int, y: int) -> bool:
    for b in ball.Ball.register:
        if b.x == x and b.y == y:
            return True
    return False


class BallShadowManager:
    def __init__(self, color: str, trail_len: int = TRAIL_LEN) -> None:
        self.max_len = trail_len + 1
        self.color = color
        self.trail = []
        
    def add(self, x: int, y: int):
        if len(self.trail) == self.max_len:
            last_x, last_y = self.trail.pop(0)
            draw_at(last_x, last_y, BLANK_SPACE, True)

        for sh_x, sh_y in self.trail:
            shadow = f"{Style.DIM}{self.color}{BALL_SHADOW}{Fore.RESET}{Style.RESET_ALL}"
            draw_at(sh_x, sh_y, shadow, True)

        self.trail.append((x, y))
        

class CollisionHighlightManager:
    def __init__(self, color: str, lifetime_ticks: int = TRAIL_LEN) -> None:
        self.color = color
        self.lifetime = lifetime_ticks
        self.highlights: list[list[int, int, int, str]] = []
        
    def add(self, x: int, y: int) -> None:
        if x == 0 and y == 0:
            char = BORDER_NW
        elif x == 0 and y == border_height+1:
            char = BORDER_SW
        elif x == border_width+1 and y == 0:
            char = BORDER_NE
        elif x == border_width+1 and y == border_height+1:
            char = BORDER_SE
        elif x == 0 or x == border_width+1:
            char = BORDER_VT
        elif y == 0 or y == border_height+1:
            char = BORDER_HZ
                
        draw_at(x, y, f"{Style.DIM}{self.color}{char}{Style.RESET_ALL}{Fore.RESET}", True)
        self.highlights.append([x, y, self.lifetime, char])
    
    def tick(self) -> None:
        filtered_hightlights = []
        
        for highlight in self.highlights:
            x, y, life, char = highlight
            highlight[2] -= 1
            
            if life <= 0:
                draw_at(x, y, f"{Fore.BLUE}{char}{Fore.RESET}")
            else:
                filtered_hightlights.append(highlight)
                
        self.highlights = filtered_hightlights
                
    
def draw_at(x: int, y: int, content: str, keep_ball: bool = False) -> None:
    if keep_ball and is_ball_at_position(x, y):
        return
    print(f"\033[{y+1};{x+1}H{content}")
     

def clear_screen():
    os.system("cls || clear")


def draw_borders(height: int, width: int, with_crosshair: bool = False):
    global border_height, border_width
    border_height = height
    border_width = width
    
    print(Fore.BLUE, end="")
    print(BORDER_NW + (BORDER_HZ * width) + BORDER_NE)

    for _ in range(height):
        print(BORDER_VT + (BLANK_SPACE * width) + BORDER_VT)

    if not with_crosshair:
        print(BORDER_SW + (BORDER_HZ * width) + BORDER_SE)
    else:
        print(BORDER_SW + (BORDER_HZ * width) + f"{Fore.RED}➷{Fore.RESET}")
    
    print(Fore.RESET)


def draw_ball(ball):
    content = f"{ball.color}{BALL_CHAR}{Fore.RESET}"                 
    draw_at(ball.x, ball.y, content)
    ball.shadow_manager.add(ball.x, ball.y)
    ball.collision_highlight_manager.tick()


def draw_stats(balls):
    draw_y = border_height + 6
    
    for ball in balls:
        draw_y += 1
        ball_icon = f"{ball.color}{BALL_CHAR}{Fore.RESET}"
        angle_info = f"{direction.get_angle_arrow_char(ball.angle)} {ball.angle}°"
        pos_info = f"[{ball.x}, {ball.y}]"
        output_content = f"{ball_icon} | {angle_info:<6} | {pos_info}"
        clear_line = " " * (len(output_content) + 5) + "\r"

        draw_at(0, draw_y, clear_line + output_content)
    
    print("                                                                     \n" * 5)        
    
    