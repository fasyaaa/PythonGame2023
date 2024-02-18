import tkinter as tk
import random

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        # increase the below value to increase the speed of ball
        self.speed = 10
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        for game_object in game_objects:
            if isinstance(game_object, Paddle):
                self.handle_paddle_collision(game_object)
            elif isinstance(game_object, Brick):
                self.handle_brick_collision(game_object)

    def handle_paddle_collision(self, paddle):
        ball_coords = self.get_position()
        paddle_coords = paddle.get_position()
        if ball_coords[2] >= paddle_coords[0] and ball_coords[0] <= paddle_coords[2] and ball_coords[3] >= paddle_coords[1] and ball_coords[1] <= paddle_coords[3]:
            paddle.animate_hit()
            self.direction[1] *= -1

    def handle_brick_collision(self, brick):
        ball_coords = self.get_position()
        brick_coords = brick.get_position()
        if ball_coords[2] >= brick_coords[0] and ball_coords[0] <= brick_coords[2] and ball_coords[3] >= brick_coords[1] and ball_coords[1] <= brick_coords[3]:
            brick.hit()
            self.direction[1] *= -1

class Paddle(GameObject):
    def __init__(self, canvas, x, y, master):
        self.width = 1000
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)
        self.master = master

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)
   
    def animate_hit(self):
        original_color = self.canvas.itemcget(self.item, 'fill')
        self.canvas.itemconfig(self.item, fill='black')
        self.master.after(100, lambda: self.canvas.itemconfig(self.item, fill=original_color))


class Brick(GameObject):
    COLORS = {1: '#4535AA', 2: '#ED639E', 3: '#8FE1A2'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits < 0:
            self.hits = 0 
        if self.hits == 0:
            self.animate_destroy()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])

    def animate_destroy(self):
        self.canvas.itemconfig(self.item, state='hidden')
        self.canvas.after(100, lambda: self.canvas.itemconfig(self.item, state='normal'))
        self.canvas.after(400, self.delete)

class PowerUp(GameObject):
    def __init__(self, canvas, x, y, color='#00FF00'):
        self.width = 20
        self.height = 20
        self.effect = self.get_random_effect()  # Metode untuk mendapatkan efek secara acak
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=color, tags='powerup')
        super(PowerUp, self).__init__(canvas, item)

    def get_random_effect(self):
        # Metode ini akan memberikan efek secara acak
        effects = ['double_ball', 'sticky_paddle', 'big_ball', 'life_up', 'fire_ball']
        return random.choice(effects)

    def apply_effect(self, game):
        # Terapkan efek dari power-up ke dalam game
        if self.effect == 'double_ball':
            # Code untuk munculkan bola tambahan
            new_ball = Ball(self.canvas, game.width / 2, 310)
            game.items[new_ball.item] = new_ball
        elif self.effect == 'sticky_paddle':
            # Code untuk membuat paddle menempel
            game.paddle.sticky = True
        elif self.effect == 'big_ball':
            # Code untuk mengubah ukuran bola menjadi lebih besar
            game.ball.radius += 5
            game.canvas.scale(game.ball.item, 0, 0, 1.25, 1.25)
        elif self.effect == 'life_up':
            # Code untuk menambah nyawa
            game.lives += 1
            game.update_lives_text()



class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326, master=self)
        self.items[self.paddle.item] = self.paddle
        # adding brick with different hit capacities - 3,2 and 1
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(10))       

    def setup_game(self):
           self.add_ball()
           self.update_lives_text()
           self.text = self.draw_text(300, 200,
                                      'Press Space to start')
           self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            self.draw_text(300, 200, 'You win! You the Breaker of Bricks.')
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'You Lose! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()