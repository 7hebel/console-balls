from direction import AngleDirection
import direction
import output


from dataclasses import dataclass


@dataclass
class WallCollisionData:
    angle: AngleDirection
    target: tuple[int, int]


class Ball:
    register: list["Ball"] = []

    def __init__(self, posy: int, posx: int, angle: int, color: str, table_height: int, table_width: int) -> None:
        self.x = posx
        self.y = posy
        self.color = color
        self.border_x = table_width
        self.border_y = table_height
        self.shadow_manager = output.BallShadowManager(color)
        self.collision_highlight_manager = output.CollisionHighlightManager(self.color)
        self.set_angle(angle)

        Ball.register.append(self)
        
    def remove(self) -> None:
        """ Remove this ball. """
        output.draw_at(self.x, self.y, output.BLANK_SPACE, False)
        
        for shadow in self.shadow_manager.trail:
            output.draw_at(shadow[0], shadow[1], output.BLANK_SPACE, True)
        
        for _ in range(self.collision_highlight_manager.lifetime):
            self.collision_highlight_manager.tick()

        if output._ball_color_index != 0:
            output._ball_color_index -= 1
        Ball.register.remove(self)
        
    def set_angle(self, new_angle: int) -> None:
        """ Safely sets new angle value. Normalizes it. """
        if new_angle < 0:
            self.angle = 360 + new_angle
        else:
            self.angle = int(new_angle % 360)
            
        self.angle = self.get_angle_direction()
        
    def set_position(self, x: int, y: int) -> None:
        """ Safely sets ball's position ensuring it stays in box. """
        if x < 0 or y < 0 or x > self.border_x or y > self.border_y:
            print(f"E:{x},{y}")
            self.x = 1
            self.y = 1
        else:
            self.x = x
            self.y = y          
            
    def get_next_position(self) -> tuple[int, int]:
        """ Calculates next ball's position according to the angle. """
        dir = self.get_angle_direction()
        x = self.x
        y = self.y
        
        if dir in direction.SOUTHISH:
            y += 1
        if dir in direction.NORTHISH:
            y -= 1
        if dir in direction.WESTISH:
            x -= 1            
        if dir in direction.EASTISH:
            x += 1    

        return (x, y)
        
    def get_angle_direction(self) -> AngleDirection:
        for dir_name in dir(AngleDirection):
            if not dir_name.startswith("__"):
                dir_value = getattr(AngleDirection, dir_name)
                dir_range = direction.calc_direction_angle_range(dir_value)

                if self.angle in dir_range:
                    return dir_value

        print(f"Error: unknown angle direction for: {self.angle}")
        return AngleDirection.S
    
    def detect_corner(self) -> tuple[bool, AngleDirection | None]:
        """ Check if ball is at the corner of the box and if, which one. """
        ball_pos = (self.x, self.y)
        corners = {
            (1, 1): AngleDirection.NW,
            (self.border_x, 1): AngleDirection.NE,
            (self.border_x, self.border_y): AngleDirection.SE,
            (1, self.border_y): AngleDirection.SW
        }
        
        if ball_pos not in corners:
            return (False, None)
        return (True, corners.get(ball_pos))
        
    def detect_wall_collisions(self) -> tuple[bool, None | list[WallCollisionData]]:
        """ Is ball next to the wall. """
        dir = self.get_angle_direction()
        collisions = []
        
        # Top:
        if dir in direction.NORTHISH:
            if self.y == 1:
                collisions.append(WallCollisionData(AngleDirection.N, (self.x, self.y-1)))
            
        # Bottom:
        if dir in direction.SOUTHISH:
            if self.y == self.border_y:
                collisions.append(WallCollisionData(AngleDirection.S, (self.x, self.y+1)))
            
        # Right:
        if dir in direction.EASTISH:
            if self.x == self.border_x:
                collisions.append(WallCollisionData(AngleDirection.E, (self.x+1, self.y)))
            
        # Left:
        if dir in direction.WESTISH:
            if self.x == 1:
                collisions.append(WallCollisionData(AngleDirection.W, (self.x-1, self.y)))

        if collisions:
            return (True, collisions)
        return (False, None)

    def handle_wall_collision(self) -> None:
        """ Adjust angle after collision. """
        is_coll, collisions = self.detect_wall_collisions()
        if not is_coll:
            return
        
        for collision in collisions:
            target_direction = collision.angle
            
            current_direction = self.get_angle_direction()
            if current_direction == target_direction:
                self.set_angle(self.angle-180)
                return

            if target_direction == AngleDirection.S:
                if self.angle < 180:
                    self.set_angle(self.angle-90)
                else:
                    self.set_angle(self.angle+90)
                
            if target_direction == AngleDirection.N:
                if self.angle < 180:
                    self.set_angle(self.angle+90)
                else:
                    self.set_angle(self.angle-90)
                
            if target_direction == AngleDirection.E:
                if self.angle < 90:
                    self.set_angle(self.angle-90)
                else:
                    self.set_angle(self.angle+90)
                    
            if target_direction == AngleDirection.W:
                if self.angle < 270:
                    self.set_angle(self.angle-90)
                else:
                    self.set_angle(self.angle+90)
      
    def detect_ball_collision(self) -> tuple[bool, list["Ball"] | None]:
        collisions = []
        next_pos = self.get_next_position()
        
        for other_ball in Ball.register:
            if other_ball == self:
                continue
            if other_ball.get_next_position() == next_pos or other_ball.x == self.x and other_ball.y == self.y:           
                collisions.append(other_ball)
                
        if collisions:
            return (True, collisions)
        return (False, None)

    def tick(self) -> None:       
        is_wall_collision, wall_collisions = self.detect_wall_collisions()
        if is_wall_collision:
            in_corner, corner = self.detect_corner()
            
            for coll_data in wall_collisions:
                if not in_corner:
                    self.collision_highlight_manager.add(coll_data.target[0], coll_data.target[1])
            
            if in_corner:     
                if corner == AngleDirection.NW:
                    self.collision_highlight_manager.add(0, 0)
                if corner == AngleDirection.NE:
                    self.collision_highlight_manager.add(self.border_x+1, 0)
                if corner == AngleDirection.SE:
                    self.collision_highlight_manager.add(self.border_x+1, self.border_y+1)
                if corner == AngleDirection.SW:
                    self.collision_highlight_manager.add(0, self.border_y+1)
                    
        self.handle_wall_collision()
        
        is_ball_collision, balls_collisions = self.detect_ball_collision()
        if is_ball_collision:
            for other_ball in balls_collisions:
                resolve_balls_collision(self, other_ball)

        self.set_position(*self.get_next_position())
        
        return True
    
    
def resolve_balls_collision(b1: Ball, b2: Ball) -> None:
    def apply_angle_change(ball: Ball, change: int) -> None:
        if ball.angle < 180:
            ball.set_angle(ball.angle + change)
        else:
            ball.set_angle(ball.angle - change)
        ball.handle_wall_collision()
    
    delta = direction.abs_sub(b1.angle, b2.angle)
    apply_angle_change(b1, delta)
    apply_angle_change(b2, delta)
    
    
    
    