from itertools import cycle
from collections import deque
import copy
import random
import sys
import time
import pygame
from pygame.locals import *

# Initialize Q-learning agent

from config import config
from q_learning import QLearning

Agent = QLearning(config['train'])

if Agent.train:
    print("Training agent...")
else:
    print("Running agent....")


# Back to game

scores = []

def printscore():
    global scores
    scores = sorted(scores)
    print("average =", sum(scores) / len(scores))
    print("midian =", scores[len(scores) // 2])

FPS = 30
SCREENWIDTH = 288
SCREENHEIGHT = 512
# amount by which base can maximum shift to left
PIPEGAPSIZE = 100  # gap between upper and lower part of pipe
BASEY = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}
STATE_HISTORY = deque(maxlen=70)  # 70 is distance between pipes
REPLAY_BUFFER = []

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)

try:
    xrange
except NameError:
    xrange = range


def main():
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    # --- TURN OFF SOUNDS ---

    # # sounds
    # if 'win' in sys.platform:
    #     soundExt = '.wav'
    # else:
    #     soundExt = '.ogg'
    #
    # SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    # SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    # SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    # SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    # SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    # time.sleep(1)

    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():

    # --- TURN OFF WELCOME ANIMATION ---

    # """Shows welcome screen animation of flappy bird"""
    # # index of player to blit on screen
    # playerIndex = 0
    # playerIndexGen = cycle([0, 1, 2, 1])
    # # iterator used to change playerIndex after every 5th iteration
    # loopIter = 0
    #
    # playerx = int(SCREENWIDTH * 0.2)
    # playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)
    #
    # messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    # messagey = int(SCREENHEIGHT * 0.12)
    #
    # basex = 0
    # # amount by which base can maximum shift to left
    # baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
    #
    # # player shm for up-down motion on welcome screen
    # playerShmVals = {'val': 0, 'dir': 1}
    #
    # while True:
    #     for event in pygame.event.get():
    #         if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
    #             pygame.quit()
    #             sys.exit()
    #         if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
    #             # make first flap sound and return values for mainGame
    #             SOUNDS['wing'].play()
    #             return {
    #                 'playery': playery + playerShmVals['val'],
    #                 'basex': basex,
    #                 'playerIndexGen': playerIndexGen,
    #             }
    #
    #     # adjust playery, playerIndex, basex
    #     if (loopIter + 1) % 5 == 0:
    #         playerIndex = next(playerIndexGen)
    #     loopIter = (loopIter + 1) % 30
    #     basex = -((-basex + 4) % baseShift)
    #     playerShm(playerShmVals)
    #
    #     # draw sprites
    #     SCREEN.blit(IMAGES['background'], (0,0))
    #     SCREEN.blit(IMAGES['player'][playerIndex],
    #                 (playerx, playery + playerShmVals['val']))
    #     SCREEN.blit(IMAGES['message'], (messagex, messagey))
    #     SCREEN.blit(IMAGES['base'], (basex, BASEY))
    #
    #     pygame.display.update()
    #     FPSCLOCK.tick(FPS)

    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)
    playerIndexGen = cycle([0, 1, 2, 1])
    return {
        'playery': playery,
        'basex': 0,
        'playerIndexGen': playerIndexGen,
    }


def mainGame(movementInfo):

    # --- REMOVE ANGULAR MOVEMENT AND SOUNDS ---

    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY = -9  # player's velocity along Y, default same as playerFlapped
    playerMaxVelY = 10  # max vel along Y, max descend speed
    playerMinVelY = -8  # min vel along Y, max ascend speed
    playerAccY = 1  # players downward accleration
    # playerRot = 45  # player's rotation
    # playerVelRot = 3  # angular speed
    # playerRotThr = 20  # rotation threshold
    playerFlapAcc = -9  # players speed on flapping
    playerFlapped = False  # True when player flaps

    # When starting the game, if we have state history to resume from then use it until it passes that pipe
    # If history is less than 20 frames this isn't enough for the bird to learn from (loop of dying) so clear the queue
    if len(STATE_HISTORY) < 20:
        STATE_HISTORY.clear()
    resume_from_history = len(STATE_HISTORY) > 0 if Agent.train else None  # only resume if training
    initial_len_history = len(STATE_HISTORY)
    resume_from = 0
    current_score = STATE_HISTORY[-1][5] if resume_from_history else None  # reset if beats the latest score in history
    print_score = False  # has the current score been printed?
    # start = time.time()
    tick = 0
    acts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    while True:
        # input()
        # print(lowerPipes)
        tick += 1
        # if tick > 100:
        #    input()
        #    pass
            
        # print(time.time() - start)
        # start = time.time()
        if resume_from_history:
            # Load from saved game history
            if resume_from < initial_len_history:
                if resume_from == 0:
                    playerx, playery, playerVelY, lowerPipes, upperPipes, score, playerIndex = \
                        STATE_HISTORY[resume_from]
                else:
                    lowerPipes, upperPipes = STATE_HISTORY[resume_from][3], STATE_HISTORY[resume_from][4]
                resume_from += 1
        else:
            # Save game history for resuming
            if Agent.train and config['resume_score'] and score >= config['resume_score']:  # only save if training
                    STATE_HISTORY.append([playerx, playery, playerVelY, copy.deepcopy(lowerPipes),
                                          copy.deepcopy(upperPipes), score, playerIndex])

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                if print_score:
                    print('')
                Agent.save_qvalues()
                Agent.save_training_states()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    # SOUNDS['wing'].play()

        # Agent to perform an action (0 is do nothing, 1 is flap)
        # timea = time.time()
        playerVelY_ = playerVelY
        if playerVelY_ < playerMaxVelY:
            playerVelY_ += playerAccY
        playerHeight_ = IMAGES['player'][playerIndex].get_height()
        playery_ = playery + min(playerVelY_, BASEY - playery - playerHeight_)

        if playerVelY_ < playerMaxVelY:
            playerVelY_ += playerAccY
        playery_ += min(playerVelY_, BASEY - playery_ - playerHeight_)    

        if playerVelY_ < playerMaxVelY:
            playerVelY_ += playerAccY
        playery_ += min(playerVelY_, BASEY - playery_ - playerHeight_)    

        # print(playerx, playery, playerVelY, lowerPipes)
        delay = 3
        lowerPipes_ = [lowerPipes[i].copy() for i in range(len(lowerPipes))]
        for i in range(len(lowerPipes_)):
            lowerPipes_[i]["x"] += delay * pipeVelX
        if lowerPipes_[0]['x'] < -IMAGES['pipe'][0].get_width():
            lowerPipes_.pop(0)

        nowact = Agent.act(playerx, playery_, playerVelY_, lowerPipes_)
        if nowact: 
            acts[delay] = 1
            #for i in range(delay, 100):
            #    if not acts[i]:
            #        acts[i] = 1
            #        break
        now = acts[0]
        acts = acts[1:]
        acts.append(0)
        # print(now)

        if now:
            acts[0] = acts[1] = acts[2] = 0
            if playery > -2 * IMAGES['player'][0].get_height():
                playerVelY = playerFlapAcc
                playerFlapped = True
        # print("agent time:", time.time() - timea)

        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes)
        if crashTest[0]:
            if print_score:
                print('')
            if resume_from_history:  # current_score is based on STATE_HISTORY
                # Managed to pass the difficult pipe
                if score > current_score:
                    Agent.update_qvalues(score)
                else:
                    REPLAY_BUFFER.append(copy.deepcopy(Agent.moves))
                # Or stuck in resume loop
                if score > current_score or len(REPLAY_BUFFER) >= 50:
                    # Update with a sample of the REPLAY_BUFFER (sample to avoid overfitting)
                    random.shuffle(REPLAY_BUFFER)
                    for _ in range(5):
                        if REPLAY_BUFFER:  # don't pop if list is empty
                            Agent.moves = REPLAY_BUFFER.pop()
                            Agent.update_qvalues(current_score)
                    STATE_HISTORY.clear()
                    REPLAY_BUFFER.clear()
            else:
                Agent.update_qvalues(score)  # only updates if training by default
            if Agent.train:
                print(f"Episode: {Agent.episode}, alpha: {Agent.alpha}, score: {score}, max_score: {Agent.max_score}")
            else:
                print(f"Episode: {Agent.episode}, score: {score}, max_score: {Agent.max_score}")
            global scores
            scores.append(score)
            if len(scores) % 100 == 0:
                printscore()
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                # 'playerRot': playerRot
            }

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                # Print every 10k scores
                if score % config['print_score'] == 0:
                    print_score = True  # need to start a newline before future prints
                    print(f"\r {'Training' if Agent.train else 'Running'} agent, "
                          f"score reached (nearest 10,000): {score:,}", end="")
                    # sys.stdout.write('\r' + f" {'Training' if Agent.train else 'Running'} "
                    #                         f"agent, score reached (nearest 10,000): {score}")
                    # sys.stdout.flush()
                # SOUNDS['point'].play()
                if config['max_score'] and score >= config['max_score']:
                    if print_score:
                        print('')
                    Agent.end_episode(score)
                    STATE_HISTORY.clear()  # don't resume if max score reached
                    REPLAY_BUFFER.clear()
                    print(f"Max score of {config['max_score']} reached at episode {Agent.episode}...")
                    return {
                        'y': playery,
                        'groundCrash': crashTest[1],
                        'basex': basex,
                        'upperPipes': upperPipes,
                        'lowerPipes': lowerPipes,
                        'score': score,
                        'playerVelY': playerVelY,
                        # 'playerRot': playerRot
                    }

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # # rotate the player
        # if playerRot > -90:
        #     playerRot -= playerVelRot

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
            # # more rotation to cover the threshold (calculated in visible rotation)
            # playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move pipes to left if done loading
        if resume_from >= initial_len_history:
            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                uPipe['x'] += pipeVelX
                lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        if config['show_game']:
            # draw sprites
            SCREEN.blit(IMAGES['background'], (0, 0))

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

            SCREEN.blit(IMAGES['base'], (basex, BASEY))
            # print score so player overlaps the score
            showScore(score)

            # # Player rotation has a threshold
            # visibleRot = playerRotThr
            # if playerRot <= playerRotThr:
            #     visibleRot = playerRot
            # playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)

            playerSurface = IMAGES['player'][playerIndex]
            SCREEN.blit(playerSurface, (playerx, playery))

            pygame.display.update()
            # print("use time", time.time() - start)
            FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo):
    """Crashes the player down and shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    # playerRot = crashInfo['playerRot']
    # playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # # play hit and die sounds
    # SOUNDS['hit'].play()
    # if not crashInfo['groundCrash']:
    #     SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                Agent.save_qvalues()
                Agent.save_training_states()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return
        return

        # ---DON'T SHOW GAMEOVER SCREEN ---

        # # player y shift
        # if playery + playerHeight < BASEY - 1:
        #     playery += min(playerVelY, BASEY - playery - playerHeight)
        #
        # # player velocity change
        # if playerVelY < 15:
        #     playerVelY += playerAccY
        #
        # # rotate only when it's a pipe crash
        # if not crashInfo['groundCrash']:
        #     if playerRot > -90:
        #         playerRot -= playerVelRot
        #
        # # draw sprites
        # SCREEN.blit(IMAGES['background'], (0, 0))
        #
        # for uPipe, lPipe in zip(upperPipes, lowerPipes):
        #     SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
        #     SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))
        #
        # SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # showScore(score)
        #
        # playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        # SCREEN.blit(playerSurface, (playerx, playery))
        # SCREEN.blit(IMAGES['gameover'], (50, 180))
        #
        # FPSCLOCK.tick(FPS)
        # pygame.display.update()


# def playerShm(playerShm):
#     """oscillates the value of playerShm['val'] between 8 and -8"""
#     if abs(playerShm['val']) == 8:
#         playerShm['dir'] *= -1
#
#     if playerShm['dir'] == 1:
#          playerShm['val'] += 1
#     else:
#         playerShm['val'] -= 1


def getRandomPipe():
    """Returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE},  # lower pipe
    ]


def showScore(score):
    """Displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0  # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """Returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                                 player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


def getHitmask(image):
    """Returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


if __name__ == '__main__':
    main()
