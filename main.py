import output
import ball
import menu

import threading
import keyboard
import random
import time

HEIGHT, WIDTH = menu.select_border_size()
TICK_COOLDOWN_S = 0.1
BALLS_AMOUNT = 1
EXIT_SIG = False

output.clear_screen()
output.draw_borders(HEIGHT, WIDTH)


for i in range(BALLS_AMOUNT):
    ball.Ball(
        random.randint(1, HEIGHT-1), 
        random.randint(1, WIDTH-1), 
        random.randint(0, 359), 
        output.wrapping_get_ball_color(), 
        HEIGHT, 
        WIDTH
    ) 


def get_safe_info_height() -> int:
    return HEIGHT + len(ball.Ball.register) + 4
    

def keyboard_control_thread():
    global TICK_COOLDOWN_S, EXIT_SIG
    
    while True:
        if keyboard.is_pressed("esc"):
            EXIT_SIG = True
            exit()
            
        if keyboard.is_pressed("r"):
            output.clear_screen()
            output.draw_borders(HEIGHT, WIDTH)
        
        if keyboard.is_pressed("down"):
            if TICK_COOLDOWN_S < 1.4:
                TICK_COOLDOWN_S += 0.05
                
        if keyboard.is_pressed("up"):
            if TICK_COOLDOWN_S > 0.06:
                TICK_COOLDOWN_S -= 0.05
                
        if keyboard.is_pressed("right"):
            if len(ball.Ball.register) < ((HEIGHT*WIDTH)/2):
                ball.Ball(
                    random.randint(1, HEIGHT-1), 
                    random.randint(1, WIDTH-1), 
                    random.randint(0, 359), 
                    output.wrapping_get_ball_color(), 
                    HEIGHT, 
                    WIDTH
                ) 
                
        if keyboard.is_pressed("left"):
            if len(ball.Ball.register) > 1:
                ball.Ball.register[-1].remove()
                
        time.sleep(0.1)
        

control_thread = threading.Thread(target=keyboard_control_thread, daemon=True)
control_thread.start()

while True:
    if EXIT_SIG:
        output.clear_screen()
        exit()
    
    time.sleep(TICK_COOLDOWN_S)
    # input()
    
    for b in ball.Ball.register:
        b.tick()
        output.draw_ball(b)
        
    output.draw_at(0, HEIGHT + 3, f"Speed: {(1/TICK_COOLDOWN_S):.2f}Hz   ")
    output.draw_at(0, HEIGHT + 4, "ESC - exit, R - refresh")
    output.draw_at(0, HEIGHT + 5, "←→ - add/remove balls, ↑↓ - speed")
    output.draw_stats(ball.Ball.register)
    
    