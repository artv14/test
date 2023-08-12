#test
import pygame
import random
import json
from sys import exit

pygame.init()


class Block:
    def __init__(self, i, j, rep, color):
        self.i = i
        self.j = j
        self.color = color
        rep.append(self)


def run():
    tile_size = 40
    tiles_x = 7
    tiles_y = 12
    window_width = tiles_x * tile_size
    window_height = tiles_y * tile_size
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption('Stacker')
    active = []
    inactive = []
    level = 0
    abs_level = level

    try:
        with open('hi_score.json') as infile:
            data = json.load(infile)
        hi_score = int(data["high_score"])  # retrieve high score from .json
    except FileNotFoundError:
        with open('hi_score.json', 'w') as newfile:  # create one if not exists
            json.dump({"high_score": 0}, newfile)  # set high score to 0
        hi_score = 0

    n = 3  # number of new blocks to be initialized
    delay = 350
    direction = 1
    color = (0, 0, 220)
    for j in range(1, n+1):
        Block(level, j, active, color)

    def draw(element):
        y = window_height - ((element.i+1) * tile_size)
        x = element.j * tile_size
        color = element.color
        rect = pygame.Rect(x, y, tile_size, tile_size)
        rect2 = pygame.Rect(x, y, tile_size, tile_size)
        pygame.draw.rect(screen, color, rect)  # solid square
        pygame.draw.rect(screen, (0, 0, 0), rect2, 2)  # black square border

    def draw_stats():
        nonlocal abs_level, hi_score, window_width
        font = pygame.font.Font(None, 20)
        hi_score_text = font.render(f'High score: {hi_score}', True, (255, 255, 255))
        score_text = font.render(f'Score: {abs_level}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))  # upper left corner (absolute)
        screen.blit(hi_score_text, (window_width-100, 10))  # upper right corner (relative)

    def advance():
        nonlocal n, active, inactive, level, abs_level, hi_score, delay, direction
        for block in active:  # check if miss
            if level != 0:
                if not any((b.j == block.j and b.i == block.i - 1) for b in inactive):  # check if block is below
                    n -= 1
                else:
                    inactive.append(block)
            else:
                inactive += active  # impossible to miss at zeroth level
        if n == 0:
            lose()
            return False
        active = []
        if level > 6:  # shift blocks down so that active remain on same level
            for block in inactive:
                block.i -= 1
        else:
            level += 1
        abs_level += 1
        delay = int(max([350 - 30 * abs_level, 50]))  # recalculate delay
        if abs_level > hi_score:  # write new high score to .json
            with open('hi_score.json', 'w') as outfile:
                new_hi_score = abs_level
                json.dump({"high_score": new_hi_score}, outfile)
                hi_score = new_hi_score

        offset = random.choice(range(3))  # randomize starting position
        for j in range(1, n + 1):  # initialize new active blocks
            if abs_level % 2 == 0:  # alternate colors to allow easier visual tracking
                color = (0, 0, 220)
            else:
                color = (0, 0, 170)
            Block(level, j + offset, active, color)
        direction = random.choice([1, -1])
        pygame.time.delay(200)  # pause briefly to show where player stopped active blocks

    def lose():
        nonlocal inactive, screen, active
        pygame.time.delay(250)  # pause to show game over
        font = pygame.font.Font(None, 30)
        font2 = pygame.font.Font(None, 20)

        for i in range(7):  # missed blocks to blink 3 times
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            for block in inactive:
                draw(block)
            if i % 2 == 0:
                for block in active:
                    draw(block)
            draw_stats()
            pygame.display.update()
            pygame.time.delay(300)

        game_over_text = font.render('Game Over', True, (255, 255, 255))
        restart_text = font2.render('Press space to play again', True, (255, 255, 255))
        screen.blit(game_over_text, (90, 150))
        pygame.display.update()
        cycle = 1
        while True:  # restart_text to blink indefinitely
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return
            if cycle == 1:
                screen.blit(restart_text, (65, 180))
                pygame.display.update()
            else:
                screen.fill((0, 0, 0))
                for block in inactive:
                    draw(block)
                for block in active:
                    draw(block)
                draw_stats()
                screen.blit(game_over_text, (90, 150))
                pygame.display.update()
            pygame.time.delay(550)
            cycle *= -1

    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    cont = advance()
                    if cont == False:
                        return

        if active[-1].j == tiles_x-1 or active[0].j == 0:  # reverse direction if hit wall
            direction *= -1

        for block in active:
            block.j += direction
            draw(block)

        for block in inactive:
            draw(block)

        draw_stats()

        pygame.display.update()
        pygame.time.delay(delay)


while True:
    run()
