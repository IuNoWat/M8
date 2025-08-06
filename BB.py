# Python imports
import random
import math

# Library imports
import pygame

# pymunk imports
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

class BouncyBalls(object):

    def __init__(self,SCREEN,FPS,radius=100) -> None:
        # Space
        self._space = pymunk.Space()
        self._space.gravity = (0.0, 1500.0)

        # Physics
        # Time step
        self._dt = 1.0 / FPS
        # Number of physics steps per screen frame
        self._physics_steps_per_frame = 1

        # pygame
        self._screen = SCREEN

        self._draw_options = pymunk.pygame_util.DrawOptions(self._screen)

        # Static barrier walls (lines) that the balls bounce off of
        self._add_static_scenery(SCREEN)

        # Balls that exist in the world
        self._balls: list[pymunk.Circle] = []

        # Ball
        self.radius=radius

    def handle_balls(self,SCREEN) :
        for x in range(self._physics_steps_per_frame):
            self._space.step(self._dt)

        #self._space.debug_draw(self._draw_options)
        for ball in self._balls :
            # image draw
            p = ball.body.position
            p = Vec2d(p.x, p.y)

            angle_degrees = math.degrees(ball.body.angle)
            rotated_logo_img = pygame.transform.rotate(ball.img_ball, angle_degrees*-1)

            offset = Vec2d(*rotated_logo_img.get_size()) / 2
            p = p - offset

            SCREEN.blit(rotated_logo_img, (round(p.x), round(p.y)))

    def _add_static_scenery(self,SCREEN) -> None:
        size=SCREEN.get_size()

        static_body = self._space.static_body
        static_lines = [
            pymunk.Segment(static_body, (0, 0), (0, size[1]), 0.0),
            pymunk.Segment(static_body, (0, size[1]), (size[0], size[1]), 0.0),
            pymunk.Segment(static_body, (size[0], size[1]), (size[0], 0), 0.0)          
        ]
        for line in static_lines:
            line.elasticity = 0.5
            line.friction = 0.9
        self._space.add(*static_lines)

    def _create_ball(self,img_ball) -> None:
        """
        Create a ball.
        :return:
        """
        mass = 5
        inertia = pymunk.moment_for_circle(mass, 0, self.radius, (0, 0))
        body = pymunk.Body(mass, inertia)
        x = random.randint(780, 820)
        body.position = x, 450
        shape = pymunk.Circle(body, self.radius, (0, 0))
        shape.elasticity = 0.7
        shape.friction = 0.9
        shape.img_ball=img_ball
        self._space.add(body, shape)
        self._balls.append(shape)


        
