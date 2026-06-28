import turtle
import time
import pygame
pygame.mixer.init()


try:
    hit_sound = pygame.mixer.Sound("assests/hit.mp3")
    wall_sound = pygame.mixer.Sound("assests/wall.mp3")
    win_sound = pygame.mixer.Sound("assests/win.mp3")
    click_sound = pygame.mixer.Sound("assests/click.mp3")  
    pygame.mixer.music.load("assests/startup.mp3") 
    
    
    hit_sound.set_volume(0.3)
    win_sound.set_volume(0.5)
    click_sound.set_volume(0.5)
    pygame.mixer.music.set_volume(0.5)
    

except pygame.error as e:
    print(f"Warning: Could not load sound file. {e}")
    
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    hit_sound = wall_sound = win_sound = click_sound = DummySound()

window = turtle.Screen()
window.title("Ping Pong by Sasa")
window.setup(width=800, height=600)
window.tracer(0)
window.bgcolor(0, 0, 0)

ball = turtle.Turtle()
ball.speed(0)
ball.shape("square")
ball.color("white")
ball.shapesize(stretch_len=1, stretch_wid=1)
ball.goto(x=0, y=0)
ball.penup()
ball_dx, ball_dy = 1, 1
ball_speed = 0.7
p1_dx, p1_dy = 0, 0
p2_dx, p2_dy = 0, 0
move_speed = 0.5

center_line = turtle.Turtle()
center_line.speed(0)
center_line.shape("square")
center_line.color("white")
center_line.shapesize(stretch_len=0.25, stretch_wid=25)
center_line.penup()
center_line.goto(0, 0)

upper_line = turtle.Turtle()
upper_line.speed(0)
upper_line.shape("square")
upper_line.color("white")
upper_line.shapesize(stretch_len=40, stretch_wid=0.1)
upper_line.penup()
upper_line.goto(0, 250)

lower_line = turtle.Turtle()
lower_line.speed(0)
lower_line.shape("square")
lower_line.shapesize(stretch_len=40, stretch_wid=.1)
lower_line.penup()
lower_line.goto(0, -250)
lower_line.color("white")

player1 = turtle.Turtle()
player1.speed(0)
player1.shape("square")
player1.shapesize(stretch_len=1, stretch_wid=5)
player1.color("blue")
player1.penup()
player1.goto(x=-350, y=0)

player2 = turtle.Turtle()
player2.speed(0)
player2.shape("square")
player2.shapesize(stretch_len=1, stretch_wid=5)
player2.color("red")
player2.penup()
player2.goto(x=350, y=0)

score = turtle.Turtle()
score.speed(0)
score.color("white")
score.penup()
score.goto(x=0, y=260)
score.write("Player1: 0 Player2: 0", align="center", font=("Courier", 14, "normal"))
score.hideturtle()

p1_score, p2_score = 0, 0

players_speed = 20

keys_pressed = {
    "w": False, "s": False, "a": False, "d": False,
    "Up": False, "Down": False, "Left": False, "Right": False
}

def press_w(): keys_pressed["w"] = True
def press_s(): keys_pressed["s"] = True
def press_a(): keys_pressed["a"] = True
def press_d(): keys_pressed["d"] = True
def press_Up(): keys_pressed["Up"] = True
def press_Down(): keys_pressed["Down"] = True
def press_Left(): keys_pressed["Left"] = True
def press_Right(): keys_pressed["Right"] = True

def release_w(): keys_pressed["w"] = False
def release_s(): keys_pressed["s"] = False
def release_a(): keys_pressed["a"] = False
def release_d(): keys_pressed["d"] = False
def release_Up(): keys_pressed["Up"] = False
def release_Down(): keys_pressed["Down"] = False
def release_Left(): keys_pressed["Left"] = False
def release_Right(): keys_pressed["Right"] = False

game_active = False
allow_click = False  

startup_title = turtle.Turtle()
startup_title.speed(0)
startup_title.penup()
startup_title.hideturtle()
startup_title.goto(0, 120)

startup_prompt = turtle.Turtle()
startup_prompt.speed(0)
startup_prompt.penup()
startup_prompt.hideturtle()
startup_prompt.goto(0, -120)

def fade_in_startup():
    global allow_click
    
 
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)
        
    allow_click = False  
    steps = 20
    for i in range(steps + 1):
        t = i / steps
        window.bgcolor(0.1 * t, 0.1 * t, 0.1 * t)
        startup_title.color(t, t, 0.0)
        startup_prompt.color(t, t, t)
        startup_title.clear()
        startup_prompt.clear()
        startup_title.write("Made by Sasa", align="center", font=("Courier", 54, "bold"))
        startup_prompt.write("Click mouse button to start", align="center", font=("Courier", 26, "italic"))
        window.update()
        time.sleep(0.04)
    allow_click = True  

def start_game(x, y):
    global game_active
    
    if not game_active and allow_click:
        click_sound.play()  
        game_active = True
        
        
        pygame.mixer.music.fadeout(500)
        
        fade_colors = ["gray", "darkgray", "#333333", "#1a1a1a"]
        for color in fade_colors:
            startup_title.color(color)
            startup_prompt.color(color)
            startup_title.clear()
            startup_prompt.clear()
            startup_title.write("Made by Sasa", align="center", font=("Courier", 54, "bold"))
            startup_prompt.write("Click mouse button to start", align="center", font=("Courier", 26, "italic"))
            window.update()
            time.sleep(0.08)
        
        startup_title.clear()
        startup_prompt.clear()
        window.update()

window.onscreenclick(start_game)
fade_in_startup()

window.listen()
window.onkeypress(press_w, "w")
window.onkeypress(press_s, "s")
window.onkeypress(press_a, "a")
window.onkeypress(press_d, "d")
window.onkeypress(press_Up, "Up")
window.onkeypress(press_Down, "Down")
window.onkeypress(press_Left, "Left")
window.onkeypress(press_Right, "Right")

canvas = window.getcanvas()
canvas.bind("<KeyRelease-w>", lambda event: release_w())
canvas.bind("<KeyRelease-s>", lambda event: release_s())
canvas.bind("<KeyRelease-a>", lambda event: release_a())
canvas.bind("<KeyRelease-d>", lambda event: release_d())
canvas.bind("<KeyRelease-Up>", lambda event: release_Up())
canvas.bind("<KeyRelease-Down>", lambda event: release_Down())
canvas.bind("<KeyRelease-Left>", lambda event: release_Left())
canvas.bind("<KeyRelease-Right>", lambda event: release_Right())

paddle_speed = 0.5

def show_winner(Wwinner_name):
    ball.hideturtle()
    center_line.hideturtle()
    lower_line.hideturtle()
    upper_line.hideturtle()
    global p1_score, p2_score, game_active
    
    
    win_sound.play()
    
    score.clear()
    colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3", "#33FFF0"]
    
    steps = 40
    for i in range(steps):
        y_pos = -300 + (i * 7.2)
        score.color(colors[i % len(colors)])
        score.clear()
        font_size = 10 + int(i * 0.5)
        score.goto(0, y_pos)
        score.write(f"🎉 {Wwinner_name} WINS!", align="center", font=("Courier", font_size, "bold"))
        window.update()
        time.sleep(0.04)

    for i in range(50):
        score.color(colors[i % len(colors)])
        score.clear()
        score.write(f"🎉 {Wwinner_name} WINS! 🎉", align="center", font=("Courier", 30, "bold"))
        window.update()
        time.sleep(0.1)
        
    p1_score, p2_score = 0, 0  
    player1.goto(-350, 0)      
    player2.goto(350, 0)
    ball.goto(0, 0)
    ball.showturtle()          
    player1.showturtle()
    player2.showturtle()
    center_line.showturtle()
    upper_line.showturtle()
    lower_line.showturtle()
    score.clear()
    score.goto(0, 260)
    score.color("white")
    score.write(f"Player1: {p1_score} Player2: {p2_score}", align="center", font=("Courier", 14, "normal"))
    
    game_active = False
    fade_in_startup()  

while True:
    window.update()
    if game_active:
        if (player1.xcor() > -30):
            player1.setx(-30)
    
        if (player1.xcor() < -380):
            player1.setx(-380)
    
        if (player1.ycor() > 200):
            player1.sety(200)
        if (player1.ycor() < -200):
            player1.sety(-200)

        if (player2.ycor() > 200):
            player2.sety(200)
        if (player2.ycor() < -200):
            player2.sety(-200)

        if (player2.xcor() < 30):
            player2.setx(30)
        if (player2.xcor() > 380):
             player2.setx(380)

        player1.setx(player1.xcor() + p1_dx)
        player1.sety(player1.ycor() + p1_dy)

        player2.setx(player2.xcor() + p2_dx)
        player2.sety(player2.ycor() + p2_dy)
    
        ball.setx(ball.xcor() + (ball_dx * ball_speed))
        ball.sety(ball.ycor() + (ball_dy * ball_speed))

        
        if (ball.ycor() > 240):
            ball.sety(240)
            ball_dy *= -1
            wall_sound.play()

        
        if (ball.ycor() < -240):
            ball.sety(-240)
            ball_dy *= -1
            wall_sound.play()

        
        if (player1.xcor() - 10 <= ball.xcor() <= player1.xcor() + 10) and (player1.ycor() - 50 < ball.ycor() < player1.ycor() + 50):
            if ball_dx < 0: 
                 ball_dx *= -1
                 hit_sound.play()

        
        if (player2.xcor() - 10 <= ball.xcor() <= player2.xcor() + 10) and (player2.ycor() - 50 < ball.ycor() < player2.ycor() + 50):
            if ball_dx > 0:
                 ball_dx *= -1
                 hit_sound.play()

        if keys_pressed["w"]: player1.sety(player1.ycor() + paddle_speed)
        if keys_pressed["s"]: player1.sety(player1.ycor() - paddle_speed)
        if keys_pressed["a"]: player1.setx(player1.xcor() - paddle_speed)
        if keys_pressed["d"]: player1.setx(player1.xcor() + paddle_speed)

        if keys_pressed["Up"]:    player2.sety(player2.ycor() + paddle_speed)
        if keys_pressed["Down"]:  player2.sety(player2.ycor() - paddle_speed)
        if keys_pressed["Left"]:  player2.setx(player2.xcor() - paddle_speed)
        if keys_pressed["Right"]: player2.setx(player2.xcor() + paddle_speed)

        if (ball.xcor() > 390):
            ball.goto(0, 0)
            ball_dx *= -1
            score.clear()
            p1_score += 1
            score.write(f"Player1: {p1_score} Player2: {p2_score}", align="center", font=("Courier", 14, "normal"))

            if p1_score == 7:
                show_winner("Player1")

        if (ball.xcor() < -390):
            ball.goto(0, 0)
            score.clear()
            ball_dx *= -1
            p2_score += 1
            score.write(f"Player1: {p1_score} Player2: {p2_score}", align="center", font=("Courier", 14, "normal"))
            if p2_score == 7:
                show_winner("player2")