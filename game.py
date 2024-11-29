import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import json
import os
import time
import random
import math
import pygame

os.system('cls')


def dump(file, item):  # Used for easily dumping information to json file
    with open(file, 'w') as f:
        json.dump(item, f, indent=4)


def load(file):  # Used for easily loading and accessing information from json file
    with open(file, 'r') as f:
        return json.load(f)


def disableMusicButtons():  # Used for disabling all music buttons
    if musicVolumeScale['state'] == 'enabled':
        musicVolumeScale['state'] = 'disabled'
    else:
        musicVolumeScale['state'] = 'enabled'


def disableSfxButtons():  # Used for disabling all sfx buttons
    if sfxVolumeScale['state'] == 'enabled':
        sfxVolumeScale['state'] = 'disabled'
    else:
        sfxVolumeScale['state'] = 'enabled'


def tempBindFunc(e):  # Used for receiving an input to create temporary bind to set custom keybinds to actions
    global shootBind, quitBind
    if e == 'Shoot':
        shootBind = root.bind('<Key>', lambda x: keybindFunc(x, 'Shoot'))
    if e == 'Quit':
        quitBind = root.bind('<Key>', lambda x: keybindFunc(x, 'Quit'))


def keybindFunc(event, arg):  # Collaborates with the previous function, receives input from the temporary bind and sets the value of the bind to a keybind
    global shootBind, quitBind, shootKeybind, quitKeybind
    if arg == 'Shoot':
        shootKeybind.set(event.keysym)
        shootKeybindButton['text'] = f'Shoot: {shootKeybind.get()}'
        root.unbind('<Key>', shootBind)
    if arg == 'Quit':
        quitKeybind.set(event.keysym)
        quitKeybindButton['text'] = f'Quit: {quitKeybind.get()}'
        root.unbind('<Key>', quitBind)


def updateSettings():  # Makes sure to update the custom keybinds
    global shootBind, quitBind,keyPress,keyRel
    shootLaserSound.set_volume(sfxVolume.get()/100)
    buttonSound.set_volume(sfxVolume.get()/100)
    explosionSound.set_volume(sfxVolume.get()/100)
    pygame.mixer.music.set_volume(musicVolume.get()/100)
    try:
        root.unbind('<Key>', shootBind)
        root.unbind('<Key>', quitBind)
    except:
        pass
    root.unbind('<Key>',keyPress)
    root.unbind('<Key>',keyRel)

    keyPress = root.bind('<KeyPress>', lambda e: bindInput(e, 'start') if e.keysym in ['a', 'A', 'd', 'D', f'{shootKeybind.get()}', f'{shootKeybind.get().upper()}', f'{quitKeybind.get()}', f'{quitKeybind.get().upper()}'] else None)
    keyRel = root.bind('<KeyRelease>', lambda e: bindInput(e, 'stop') if e.keysym in ['a', 'A', 'd', 'D', f'{shootKeybind.get()}', f'{shootKeybind.get().upper()}'] else None)


def updateShip():  # Updates the image of the ship, giving it more life
    global player, spaceship1Img, spaceship2Img, shipImage
    if shipImage == 1:
        canvas.itemconfig(player, image=spaceship1Img)
        shipImage = 2
    elif shipImage == 2:
        canvas.itemconfig(player, image=spaceship2Img)
        shipImage = 1
    if gameRunning:
        root.after(100, updateShip)


def saveFunc(e):  # Saves all data about the player in a json file
    global kills, shotCounter, shotsHit
    root.destroy()
    settings = {
        'difficulty': difficulty.get(),
        'music': music.get(),
        'musicVolume': musicVolume.get(),
        'sfx': sfx.get(),
        'sfxVolume': sfxVolume.get(),
        'shootKeybind': shootKeybind.get(),
        'quitKeybind': quitKeybind.get(),
        'lifetimeKills': lifetimeKills.get() + kills,
        'lifetimeGames': lifetimeGames.get() + gamesPlayed,
        'lifetimeShots': lifetimeShots.get() + shotCounter,
        'totalShotsHit': totalShotsHit.get() + shotsHit,
        'highscore': highscore.get() if highscore.get() > score else score,
        'accuracy': f'{round(((totalShotsHit.get()+shotsHit)/(lifetimeShots.get()+shotCounter))*100,2)}%' if lifetimeShots.get()+shotsHit != 0 else '0.0%'
    }
    dump('data.json', settings)


def motion(event):  # Retrieves the x position of the mouse whenever motion on the mouse is detected
    global mouseX
    mouseX = event.x


# Changes the direction of the player when 'a' or 'd' is pressed
def bindInput(event, action):
    global playerMovement, moveRight, moveLeft, isShooting
    if action == 'start':
        if event.keysym in ['a', 'A']:
            moveLeft = True
            moveRight = False
        elif event.keysym in ['d', 'D']:
            moveRight = True
            moveLeft = False
        elif event.keysym in [f'{shootKeybind.get()}', f'{shootKeybind.get().upper()}']:
            isShooting = True
        elif event.keysym in [f'{quitKeybind.get()}', f'{quitKeybind.get().upper()}']:
            saveFunc('e')
    elif action == 'stop':
        if event.keysym in ['a', 'A']:
            moveLeft = False
        elif event.keysym in ['d', 'D']:
            moveRight = False
        elif event.keysym in [f'{shootKeybind.get()}', f'{shootKeybind.get().upper()}']:
            isShooting = False
    if moveRight and not moveLeft:
        playerMovement = 3
    elif not moveRight and moveLeft:
        playerMovement = -3
    else:
        playerMovement = 0


def initializeGame():  # Main initializer for starting the actual game
    global gamesPlayed, gameRunning, playerHealth, removeAfter, updateShipAfter, moveEnemiesAfter, gameLoopAfter
    startingFrame.pack_forget()
    pygame.mixer.music.stop()
    pygame.mixer.music.load('Assets/Game music.wav')
    pygame.mixer.music.play(-1)
    gameRunning = True
    playerHealth = 3
    gamesPlayed += 1
    canvas.pack()
    root.geometry('1200x800')
    for i in range(55):
        exec(f'alien{i} = Aliens()')
    Aliens.spawn()
    removeAfter = root.after(10, remove)
    updateShipAfter = root.after(10, updateShip)
    moveEnemiesAfter = root.after(10, moveEnemies)
    gameLoopAfter = root.after(10, gameLoop)


def shoot(event):  # Shoots lasers from the ship when keybind is pressed
    global shotCounter, startTime, endTime, isShooting
    endTime = time.time()
    differenceTime = endTime - startTime
    if differenceTime >= 0.5 and isShooting == True:
        shootLaserSound.play()
        shotCounter += 1
        exec(
            f'a{shotCounter} = canvas.create_rectangle(canvas.coords(player)[0], 600, canvas.coords(player)[0]+5, 570,fill="red")')
        exec(f'shots.append(a{shotCounter})')
        startTime = time.time()


def remove():  # Creates explosion when alien is destroyed
    global explosion1Img, explosion2Img, explosion3Img, explosion4Img, alienRemoveList, kills, alienList
    startTime = time.time()
    for key in alienRemoveList:
        if time.time() - alienRemoveList[key] >= 0 and time.time() - alienRemoveList[key] <= 0.2:
            canvas.itemconfig(key.body, image=explosion1Img)
        elif time.time() - alienRemoveList[key] >= 0.2 and time.time() - alienRemoveList[key] <= 0.4:
            canvas.itemconfig(key.body, image=explosion2Img)
        elif time.time() - alienRemoveList[key] >= 0.4 and time.time() - alienRemoveList[key] <= 0.6:
            canvas.itemconfig(key.body, image=explosion3Img)
        else:
            canvas.delete(key.body)
    if gameRunning:
        root.after(10, remove)

def resetGame():
    global gameRunning, alienCount, shots, alienShootList, alienList, alienShootCounter, enemyMoveSpeed, score, highscore, playerHealth
    pygame.mixer.music.stop()
    pygame.mixer.music.load('Assets/Menu music.wav')
    pygame.mixer.music.play(-1)
    highscore.set(score) if score > highscore.get() else None
    playerHealth = 0
    score = 0
    alienCount = 0
    enemyMoveSpeed = 500
    alienShootCounter = 0
    for bullet in shots:
        canvas.delete(bullet)
    shots.clear()
    for enemyBullet in alienShootList:
        canvas.delete(enemyBullet)
    alienShootList.clear()
    for alien in alienList:
        canvas.delete(alien.body)
    alienList.clear()
    gameRunning = False
    root.after_cancel(removeAfter)
    root.after_cancel(updateShipAfter)
    root.after_cancel(moveEnemiesAfter)
    root.after_cancel(gameLoopAfter)
    canvas.pack_forget()
    gameOverFrame.pack()
    root.geometry('400x400')


def moveEnemies():  # Makes the enemies able to move in a certain pattern
    global enemyVel, enemyMoveOpposite, enemyMoveSpeed, enemyMoveRootAfter, alienShootCounter, alienShootList
    if gameRunning:
        alienShootCounter += 1
        if enemyMoveOpposite:
            for alien in alienList:
                canvas.move(alien.body, enemyVel, 0)
            enemyMoveOpposite = False
        else:
            moveDown = False
            for alien in alienList:
                if canvas.coords(alien.body)[0]+25 >= 1175 or canvas.coords(alien.body)[0]-25 <= 25:
                    moveDown = True
                    break
            if moveDown:
                for alien in alienList:
                    canvas.move(alien.body, 0, 50)
                if canvas.coords(alien.body)[1]+25 >= 600:
                    resetGame()
                enemyVel *= -1
                enemyMoveOpposite = True
            else:
                for alien in alienList:
                    if canvas.coords(alien.body)[0]+25 < 1175 and enemyVel > 0 and not enemyMoveOpposite:
                        canvas.move(alien.body, enemyVel, 0)
                    elif canvas.coords(alien.body)[0]-25 > 25 and enemyVel < 0 and not enemyMoveOpposite:
                        canvas.move(alien.body, enemyVel, 0)
        if alienShootCounter % 4 == 0 and gameRunning:
            alienShooter = alienList[random.randint(
                0, len(alienList)-1 if len(alienList) >= 1 else 0)]
            exec(
                f'alienShot{alienShootCounter}=canvas.create_rectangle(canvas.coords(alienShooter.body)[0]-3, canvas.coords(alienShooter.body)[1]+20, canvas.coords(alienShooter), canvas.coords(alienShooter.body)[0]+3, canvas.coords(alienShooter.body)[1]+50, fill="green")')
            exec(f'alienShootList.append(alienShot{alienShootCounter})')
    if gameRunning:
        enemyMoveRootAfter = root.after(math.ceil(enemyMoveSpeed), moveEnemies)


def gameLoop():  # Main loop of the game, makes everything move and work
    global playerMovement, shotCounter, shotsHit, kills, enemyMoveSpeed, enemyMoveRootAfter, alienRemoveList, enemyVel, alienShootList, playerHealth, gameRunning, alienCount, score, scoreDisplay
    canvas.move(player, playerMovement, 0)
    if canvas.coords(player)[0]-37.5 < 0 or canvas.coords(player)[0]+37.5 > 1200:
        canvas.move(player, playerMovement*-1, 0)
    shoot('e')
    if len(alienList) <= 0:
        for enemyBullet in alienShootList:
            canvas.delete(enemyBullet)
        alienShootList.clear()
        for bullet in shots:
            canvas.delete(bullet)
        shots.clear()
        playerHealth += 1 if playerHealth != 3 else 0
        if gameRunning:
            score += 150
        enemyMoveSpeed *= 0.9
        enemyVel = 12.5
        root.after_cancel(enemyMoveRootAfter)
        enemyMoveRootAfter = root.after(
            math.ceil(enemyMoveSpeed), moveEnemies)
        if gameRunning:
            alienCount = 0
            for i in range(55):
                exec(f'alien{i} = Aliens()')
            Aliens.spawn()
    for enemyBullet in alienShootList:
        canvas.move(enemyBullet, 0, 4)

        if canvas.coords(enemyBullet)[1] > 800:
            canvas.delete(enemyBullet)
            alienShootList.remove(enemyBullet)
            break
        if (int(canvas.coords(enemyBullet)[0]) in range(int(canvas.coords(player)[0]-37.5), int(canvas.coords(player)[0]+37.5))):
            if (int(canvas.coords(enemyBullet)[1]) in range(int(canvas.coords(player)[1]-30), int(canvas.coords(player)[1]+37.5))):
                canvas.delete(enemyBullet)
                alienShootList.remove(enemyBullet)
                playerHealth -= 1
                if playerHealth <= 0:
                    root.after_cancel(root)
                    root.after(50, resetGame)
                    break
                break
    for bullet in shots:
        canvas.move(bullet, 0, -6)
        for enemy in alienList:
            if canvas.coords(bullet)[0] in range(int(canvas.coords(enemy.body)[0]-37.5), int(canvas.coords(enemy.body)[0]+37.5)) and canvas.coords(bullet)[1] in range(int(canvas.coords(enemy.body)[1]-37.5), int(canvas.coords(enemy.body)[1]+10)):
                enemy.health -= 1
                shotsHit += 1
                canvas.move(bullet, 0, -1000)
            if enemy.health <= 0:
                exec(f'alienRemoveList[enemy] = time.time()')
                explosionSound.play()
                score += 15
                kills += 1
                alienList.remove(enemy)
    for bullet in shots:
        if canvas.coords(bullet)[1] < 10:
            shots.remove(bullet)
            canvas.delete(bullet)
    canvas.itemconfig(scoreDisplay, text=f'Score {score}')
    canvas.itemconfig(playerHealthDisplay, text=f'Lives {playerHealth}')
    if gameRunning:
        root.after(10, gameLoop)


def updateVolume(e):  # Update the volume of the game displays
    musicVolumeDisplay['text'] = f'Music volume: {musicVolume.get()}'
    sfxVolumeDisplay['text'] = f'Sfx volume: {sfxVolume.get()}'


class Aliens:  # Alien class, easy access to information about each object of the class
    def __init__(self):
        self.health = int(difficulty.get())
        self.index = len(alienList)
        alienList.append(self)

    def spawn():
        global alienCount
        for i in range(5):
            for j in range(11):
                alienList[alienCount].body = canvas.create_image(
                    100+j*65, 50+i*70, image=alienImg)
                alienCount += 1


if __name__ == '__main__':  # Main code in the program

    # Define root and canvas

    root = ttk.Window(themename='superhero')
    root.geometry('500x600+300+50')
    root.title('Space Invader')
    canvas = tk.Canvas(root, width=1200, height=800)
    root.resizable(False, False)

    # Create variables and import from data.json

    startTime = 1  # Counts time between shots
    endTime = 0  # Counts time between shots

    gameRunning = False  # Used as flag when game is not running

    kills = 0  # Count kills
    playerHealth = 3  # Health of player
    playerMovement = 0  # Speed of player
    shipImage = 1  # Image of player, animates ship
    gamesPlayed = 0  # Count how many games the player has played
    isShooting = False  # Checks if the player is shooting or not
    moveRight = False  # Checks of player is moving right
    moveLeft = False  # Checks if player is moving left
    score = 0  # Player's score

    alienList = []  # List of all enemies that are alive
    alienShootList = []  # List of all enemy bullets
    # Dict of all enemies that have been destroyed, creates death animation
    alienRemoveList = {}
    alienShootCounter = 0  # Number of enemy shots
    alienCount = 0  # Number of aliens
    enemyVel = 12.5  # Velocity of enemies
    enemyMoveOpposite = False  # True if enemies are supposed to change direction
    enemyMoveSpeed = 500  # Speed of which enemies move
    enemyMoveRootAfter = None  # Variable for after function of enemy movements

    # Importing variables from data.json (names of variables make it pretty obvious what they do)

    shootKeybind = tk.StringVar(value=load('./data.json')['shootKeybind'])
    lifetimeKills = tk.IntVar(value=load('./data.json')['lifetimeKills'])
    quitKeybind = tk.StringVar(value=load('./data.json')['quitKeybind'])
    music = tk.BooleanVar(value=load('./data.json')['music'])
    musicVolume = tk.IntVar(value=load('./data.json')['musicVolume'])
    sfx = tk.BooleanVar(value=load('./data.json')['sfx'])
    sfxVolume = tk.IntVar(value=load('./data.json')['sfxVolume'])
    difficulty = tk.StringVar(value=load('./data.json')['difficulty'])
    lifetimeGames = tk.IntVar(value=load('./data.json')['lifetimeGames'])
    lifetimeShots = tk.IntVar(value=load('./data.json')['lifetimeShots'])
    highscore = tk.IntVar(value=load('./data.json')['highscore'])
    totalShotsHit = tk.IntVar(value=load('./data.json')['totalShotsHit'])

    shots = []  # List of all the current player shots
    shotCounter = 0  # Number of shots fired
    shotsHit = 0  # Number of shots hit

    # Enables and disables music/sfx buttons

    disableMusicButton = 'enabled'
    disableSfxButton = 'enabled'
    if sfx.get() == False:
        disableSfxButton = 'disabled'
    if music.get() == False:
        disableMusicButton = 'disabled'

    # Use all assets as images for game objects

    image = Image.open('Assets/Alien.png')
    img = image.resize((50, 50))
    alienImg = ImageTk.PhotoImage(img)

    image = Image.open('Assets/Explosion1.png')
    img = image.resize((50, 50))
    explosion1Img = ImageTk.PhotoImage(img)

    image = Image.open('Assets/Explosion2.png')
    img = image.resize((50, 50))
    explosion2Img = ImageTk.PhotoImage(img)

    image = Image.open('Assets/Explosion3.png')
    img = image.resize((50, 50))
    explosion3Img = ImageTk.PhotoImage(img)

    image = Image.open('Assets/Explosion4.png')
    img = image.resize((50, 50))
    explosion4Img = ImageTk.PhotoImage(img)

    image = Image.open('Assets/Spaceship1.png')
    img = image.resize((75, 75))
    spaceship1Img = ImageTk.PhotoImage(img)

    image = Image.open('Assets/Spaceship2.png')
    img = image.resize((75, 75))
    spaceship2Img = ImageTk.PhotoImage(img)

    image = Image.open('Assets/spaceBackground.png')
    img = image.resize((1200, 800))
    bgImg = ImageTk.PhotoImage(img)

    pygame.init()

    shootLaserSound = pygame.mixer.Sound('Assets/Laser sound.wav')
    buttonSound = pygame.mixer.Sound('Assets/Button sound.wav')
    explosionSound = pygame.mixer.Sound('Assets/Explosion sound.wav')

    shootLaserSound.set_volume(sfxVolume.get()/100)
    buttonSound.set_volume(sfxVolume.get()/100)
    explosionSound.set_volume(sfxVolume.get()/100)

    pygame.mixer.music.set_volume(musicVolume.get()/100)

    pygame.mixer.music.load('Assets/Menu music.wav')
    pygame.mixer.music.play(-1)

    # Create player

    canvas.create_image(600, 400, image=bgImg)
    player = canvas.create_image(600, 640, image=spaceship1Img)
    scoreDisplay = canvas.create_text(1100, 750, text=f'Score {score}', font='helvetica 18 bold', fill='white')
    playerHealthDisplay = canvas.create_text(100, 750, text=f'Lives {playerHealth}', font='helvetica 18 bold', fill='white')

    # Create the main menu frame

    startingFrame = ttk.Frame(root)
    startingFrame.pack(pady=20, padx=50)

    mainLabel = ttk.Label(startingFrame, text='Welcome to SpaceInvader!', font='helvetica 18 bold')

    difficultyLabel = ttk.Label(startingFrame, text='Select a difficulty', font='helvetica 16')

    easy = ttk.Radiobutton(startingFrame, text='Easy', value='1', variable=difficulty)
    medium = ttk.Radiobutton(startingFrame, text='Medium', value='2', variable=difficulty)
    hard = ttk.Radiobutton(startingFrame, text='Hard', value='3', variable=difficulty)
    impossible = ttk.Radiobutton(startingFrame, text='Impossible', value='4', variable=difficulty)

    mainLabel.pack(pady=40, padx=0)
    difficultyLabel.pack(pady=15)
    easy.pack(pady=20, padx=150, anchor='w')
    medium.pack(pady=20, padx=150, anchor='w')
    hard.pack(pady=20, padx=150, anchor='w')
    impossible.pack(pady=20, padx=150)

    initialize = ttk.Button(startingFrame, text='Play', width=8, command=initializeGame).pack(pady=20, padx=5)

    settingsButton = ttk.Button(startingFrame, text='Settings', bootstyle='light', width=8, command=lambda: [startingFrame.pack_forget(), settingsFrame.pack(padx=50, pady=30), keybindFrame.pack(pady=(10, 20), padx=20), settingBackButton.pack(pady=(10, 30), padx=50, side=tk.BOTTOM, anchor=tk.W)]).pack(side='left', padx=10, pady=10)

    statsButton = ttk.Button(startingFrame, text='Stats', bootstyle='light', width=8, command=lambda: [statsFrame.pack(), startingFrame.pack_forget(), statsBackButton.pack(pady=50, padx=50, side=tk.BOTTOM)])

    # Create settings menu

    settingsFrame = ttk.Frame(root)

    # Create sounds label

    soundsLabel = ttk.Label(settingsFrame, text='Sounds', font='helvetica 18 bold')

    # Pack sounds label

    soundsLabel.pack(pady=20, side=tk.TOP)

    # Create settings for music

    musicSetting = ttk.Checkbutton(settingsFrame, bootstyle='round-toggle', text='Music On/Off', variable=music, command=disableMusicButtons)
    musicVolumeDisplay = ttk.Label(settingsFrame, text=f'Music volume: {musicVolume.get()}')
    musicVolumeScale = ttk.Scale(settingsFrame, length=300, from_=0, to=100, state=disableMusicButton, orient='horizontal', variable=musicVolume, command=updateVolume)

    # Pack music settings

    musicSetting.pack(pady=5)
    musicVolumeDisplay.pack(pady=5)
    musicVolumeScale.pack(pady=5)

    # Create settings for sfx

    sfxSetting = ttk.Checkbutton(settingsFrame, bootstyle='round-toggle', text='Sfx On/Off', variable=sfx, command=disableSfxButtons)
    sfxVolumeDisplay = ttk.Label(settingsFrame, text=f'Sfx volume: {sfxVolume.get()}')
    sfxVolumeScale = ttk.Scale(settingsFrame, length=300, from_=0, to=100, state=disableSfxButton, orient='horizontal', variable=sfxVolume, command=updateVolume)

    # Pack sfx settings

    sfxSetting.pack(pady=(35, 5))
    sfxVolumeDisplay.pack(pady=5)
    sfxVolumeScale.pack(pady=5)

    # Create frame for keybinds

    keybindFrame = ttk.Frame(root, bootstyle='superhero')

    # Create buttons to change keybinds

    keybindLabel = ttk.Label(keybindFrame, text='Keybinds', font='helvetica 18 bold')

    shootKeybindButton = ttk.Button(keybindFrame, text=f'Shoot: {shootKeybind.get()}', width=12, command=lambda: tempBindFunc('Shoot'))

    quitKeybindButton = ttk.Button(keybindFrame, text=f'Quit: {quitKeybind.get()}', width=12, command=lambda: tempBindFunc('Quit'))

    # Pack keybind settings

    keybindLabel.pack(pady=20, side=tk.TOP)
    shootKeybindButton.pack(pady=10, padx=20, side=tk.RIGHT)
    quitKeybindButton.pack(pady=10, padx=20, side=tk.LEFT)

    # Create back button

    settingBackButton = ttk.Button(root, text='Save and back', command=lambda: [updateSettings(), keybindFrame.pack_forget(), settingsFrame.pack_forget(), startingFrame.pack(), settingBackButton.pack_forget()])

    # Create stats frame

    statsFrame = ttk.Frame(root)

    statsBackButton = ttk.Button(root, text='Back', width=100, command=lambda: [statsFrame.pack_forget(), startingFrame.pack(), statsBackButton.pack_forget()])

    statisticsLabel = ttk.Label(statsFrame, text='Statistics', font='helvetica 30 bold').pack(pady=20, side=tk.TOP)

    statsLabel = ttk.Label(statsFrame, text=f'Highscore: {highscore.get()}\n\nAccuracy: {round(lifetimeKills.get()/lifetimeShots.get()*100,2) if lifetimeShots.get() != 0 else 0.00}%\n\nLifetime games: {lifetimeGames.get()}\n\nLifetime kills: {lifetimeKills.get()}\n\nLifetime shots: {lifetimeShots.get()}', font=('Small fonts', 20))

    statsButton.pack(padx=20, pady=10, side='right')
    statsLabel.pack(pady=5, padx=18)

    # Create game over frame

    gameOverFrame = ttk.Frame(root)

    gameOverLabel = ttk.Label(gameOverFrame, text='Game Over', font='calibri 30 bold').pack(pady=(20, 40))

    highscoreLabel = ttk.Label(gameOverFrame, text=f'Highscore: {highscore.get() if highscore.get() > score else score}', font='helvetica 20 italic').pack(pady=20)

    menuButton = ttk.Button(gameOverFrame, text='Main Menu', width=12, command=lambda: [gameOverFrame.pack_forget(), root.geometry('500x600+300+50'), startingFrame.pack()]).pack(pady=20)

    quitButton = ttk.Button(gameOverFrame, text='Quit', width=12, command=lambda: saveFunc('e')).pack(pady=20)

    # Bind keybinds and other functions to root

    keyPress = root.bind('<KeyPress>', lambda e: bindInput(e, 'start')if e.keysym in ['a', 'A', 'd', 'D', f'{shootKeybind.get()}', f'{shootKeybind.get().upper()}', f'{quitKeybind.get()}', f'{quitKeybind.get().upper()}'] else None)
    keyRel = root.bind('<KeyRelease>', lambda e: bindInput(e, 'stop') if e.keysym in ['a', 'A', 'd', 'D', f'{shootKeybind.get()}', f'{shootKeybind.get().upper()}'] else None)

    root.bind('<Motion>', motion)

    root.protocol('WM_DELETE_WINDOW', lambda: print(f'Exit the program by pressing {quitKeybind.get()} on your keyboard.'))
    root.mainloop()
