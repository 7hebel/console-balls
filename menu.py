import output
import keyboard
import time


def select_border_size() -> tuple[int, int]:
    height = 5
    width = 10
    
    INFO_TEXT = "Use arrows to resize border, enter to apply."
    
    output.clear_screen()
    print(INFO_TEXT)
    output.draw_borders(height, width, True)
    
    changed = False
    
    while True:
        if keyboard.is_pressed("enter"):
            return height, width
        
        if keyboard.is_pressed("left"):
            if width > 3:
                width -= 1
                changed = True
                
        if keyboard.is_pressed("right"):
            if width < 60:
                width += 1
                changed = True
                
        if keyboard.is_pressed("up"):
            if height > 3:
                height -= 1
                changed = True
                
        if keyboard.is_pressed("down"):
            if height < 25:
                height += 1
                changed = True
                
        if changed:
            output.clear_screen()
            print(INFO_TEXT)
            output.draw_borders(height, width, True)
            changed = False
            
        time.sleep(0.1)
        



