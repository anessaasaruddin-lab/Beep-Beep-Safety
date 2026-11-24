import pygame
import random
import math
import time
import sys


class SimulationScene:
    def __init__(self, screen):
        pygame.init()
        pygame.mixer.init()

        self.screen = screen
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True

        # ================= ASSETS =================
        self.background = pygame.transform.smoothscale(
            pygame.image.load("background.png").convert(),
            (self.WIDTH, self.HEIGHT)
        )

        self.player_img = pygame.transform.scale(
            pygame.image.load("character.png").convert_alpha(), (50, 50)
        )

        self.car_img = pygame.transform.scale(
            pygame.image.load("orangecar.png").convert_alpha(), (80, 40)
        )

        self.up_img = pygame.transform.scale(
            pygame.image.load("up_button.png").convert_alpha(), (110, 110)
        )
        self.down_img = pygame.transform.scale(
            pygame.image.load("down_button.png").convert_alpha(), (110, 110)
        )

        self.retry_img = pygame.transform.scale(
            pygame.image.load("retry_button.png").convert_alpha(), (200, 80)
        )
        self.next_img = pygame.transform.scale(
            pygame.image.load("next_button.png").convert_alpha(), (100, 80)
        )

        self.red_light = pygame.transform.scale(
            pygame.image.load("traffic_red.png").convert_alpha(), (250, 320)
        )
        self.yellow_light = pygame.transform.scale(
            pygame.image.load("traffic_yellow.png").convert_alpha(), (250, 320)
        )
        self.green_light = pygame.transform.scale(
            pygame.image.load("traffic_green.png").convert_alpha(), (250, 320)
        )

        self.ped_red = pygame.transform.scale(
            pygame.image.load("ped_red.png").convert_alpha(), (190, 210)
        )
        self.ped_yellow = pygame.transform.scale(
            pygame.image.load("ped_yellow.png").convert_alpha(), (190, 210)
        )
        self.ped_green = pygame.transform.scale(
            pygame.image.load("ped_green.png").convert_alpha(), (190, 210)
        )
        self.answer_img = pygame.transform.scale(
            pygame.image.load("answer_btn.png").convert_alpha(),
            (150, 65)
        )
        self.decline_img = pygame.transform.scale(
            pygame.image.load("decline_btn.png").convert_alpha(),
            (150, 65)
        )


        # ================= SOUNDS =================
        self.click_sound = pygame.mixer.Sound("click.wav")
        self.gameover_sound = pygame.mixer.Sound("over.mp3")
        self.success_sound = pygame.mixer.Sound("win.mp3")
        self.phone_sound = pygame.mixer.Sound("ring.mp3")
        self.traffic_sound = pygame.mixer.Sound("traffic.wav")
        self.rain_sound = pygame.mixer.Sound("rain.mp3")

        self.traffic_sound.play(-1)

        # ================= FONTS =================
        self.font_small = pygame.font.Font("pixel_font.otf", 25)
        self.font_big = pygame.font.Font("pixel_font.otf", 80)

        # ================= PLAYER =================
        self.player_start_x = self.WIDTH // 2 - 40
        self.player_start_y = 390
        self.player_x = self.player_start_x
        self.player_y = self.player_start_y
        self.PLAYER_SPEED = 2

        # ================= GAME AREA =================
        self.FINISH_Y = 90
        self.CROSSING_X = self.WIDTH // 2 - 40
        self.CROSSING_W = 280
        self.CROSSING_START_Y = 250
        self.CROSSING_END_Y = 280

        # ================= STOP LINES (for cars) =================
        self.STOP_LINE_LEFT = self.CROSSING_X - 8
        self.STOP_LINE_RIGHT = self.CROSSING_X + self.CROSSING_W + 8


        # ================= VEHICLES =================
        self.vehicles = []
        self.spawn_vehicles()

        # ================= TRAFFIC LIGHTS =================
        self.CAR_GREEN = 7
        self.CAR_YELLOW = 3
        self.CAR_RED = 20
        self.cycle = self.CAR_GREEN + self.CAR_YELLOW + self.CAR_RED
        self.light_timer = 0.0

        #green timer
        self.GREEN_TIMER_START = 20.0
        self.green_timer = self.GREEN_TIMER_START
        self.green_timer_running = False

        # ================= UI =================
        self.up_rect = pygame.Rect(50, 420, 120, 120)
        self.down_rect = pygame.Rect(200, 420, 120, 120)

        self.retry_rect = pygame.Rect(
            self.WIDTH//2 - 100, self.HEIGHT//2 + 40, 200, 80
        )
        self.next_rect = self.next_img.get_rect(
            center=(self.WIDTH//2, self.HEIGHT//2 + 80)
        )

        # ================= TOGGLES =================
        self.toggle_font = pygame.font.Font("pixel_font.otf", 20)
        self.toggle_rects = {
            "DAY": pygame.Rect(20, 20, 100, 40),
            "NIGHT": pygame.Rect(140, 20, 100, 40),
            "RAIN": pygame.Rect(260, 20, 100, 40),
        
        }

        self.is_night = False
        self.is_rain = False
        self.headlights_on = False

        # ================= RAIN =================
        self.rain_particles = []

        # ================= PHONE EVENT =================
        self.phone_active = False
        self.phone_timer = 0.0
        self.phone_triggered = False
        self.phone_duration = 3.0

        # ================= PHONE BUTTON RECTS =================
        self.answer_rect = self.answer_img.get_rect(
            center=(self.WIDTH//2 - 85, self.HEIGHT//2 + 60)
        )

        self.decline_rect = self.decline_img.get_rect(
            center=(self.WIDTH//2 + 85, self.HEIGHT//2 + 60)
        )

        # ================= GAME STATE =================
        self.game_over = False
        self.game_over_msg = ""
        self.show_retry = False
        self.success = False
        self.hover_next_played = False

    # =====================================================
    def spawn_vehicles(self):
        self.vehicles = []

        # Top lane (→ right)
        self.vehicles.append({
            "x": -100,
            "y": 180,
            "dir": 1,
            "speed": random.uniform(2.0, 4.0),
            "w": 80,
            "h": 40,
            "stopped": False
        })

        # Bottom lane (← left)
        self.vehicles.append({
            "x": self.WIDTH + 100,
            "y": 320,
            "dir": -1,
            "speed": random.uniform(2.0, 4.0),
            "w": 80,
            "h": 40,
            "stopped": False
        })
    
    def car_light_state(self):
        t = self.light_timer % self.cycle
        if t < self.CAR_GREEN: return "GREEN"
        if t < self.CAR_GREEN + self.CAR_YELLOW: return "YELLOW"
        return "RED"

    def ped_light_state(self):
        s = self.car_light_state()
        if s == "RED": return "GREEN"
        if s == "YELLOW": return "YELLOW"
        return "RED"

    def update_vehicles(self, dt, car_state):
        for v in self.vehicles:
            # Determine stop position
            if v["dir"] == 1:
                stop_x = self.STOP_LINE_LEFT - v["w"] - 6
                approaching = v["x"] + v["w"] < self.STOP_LINE_LEFT + 140
            else:
                stop_x = self.STOP_LINE_RIGHT + 6
                approaching = v["x"] > self.STOP_LINE_RIGHT - 140

            if car_state == "RED" and approaching:
                v["stopped"] = True
                if v["dir"] == 1 and v["x"] < stop_x:
                    v["x"] += min(v["speed"] * 0.3, stop_x - v["x"])
                if v["dir"] == -1 and v["x"] > stop_x:
                    v["x"] -= min(v["speed"] * 0.3, v["x"] - stop_x)

            elif car_state == "YELLOW":
                v["stopped"] = False
                v["x"] += v["dir"] * v["speed"] * 0.45 * dt * 60

            else:  # GREEN
                v["stopped"] = False
                v["x"] += v["dir"] * v["speed"] * dt * 60

            # Respawn
            if v["dir"] == 1 and v["x"] > self.WIDTH + 300:
                v["x"] = -300
            if v["dir"] == -1 and v["x"] < -300:
                v["x"] = self.WIDTH + 300


    # =====================================================
    def spawn_rain(self):
        while len(self.rain_particles) < 500:
            self.rain_particles.append([
                random.randint(0, self.WIDTH),
                random.randint(-100, 0),
                random.uniform(4, 8),
                random.randint(8, 15)
            ])

    def update_rain(self):
        for d in self.rain_particles:
            d[1] += d[2]
        self.rain_particles = [d for d in self.rain_particles if d[1] < self.HEIGHT]

    def draw_rain(self):
        for d in self.rain_particles:
            pygame.draw.line(self.screen, (170,170,200), (d[0], d[1]), (d[0], d[1]+d[3]), 1)

    # =====================================================
    def reset_all(self):
        self.player_x = self.player_start_x
        self.player_y = self.player_start_y
        self.game_over = False
        self.success = False
        self.show_retry = False
        self.game_over_msg = ""
        self.hover_next_played = False
        self.phone_active = False
        self.phone_triggered = False
        self.phone_timer = 0.0
        self.light_timer = 0.0
        self.spawn_vehicles()

    # =====================================================
    def draw_hoverable_button(self, rect, image, scale=1.1):
        mx, my = pygame.mouse.get_pos()
        if rect.collidepoint(mx, my):
            w, h = rect.size
            img = pygame.transform.smoothscale(image, (int(w*scale), int(h*scale)))
            self.screen.blit(img, img.get_rect(center=rect.center))
        else:
            self.screen.blit(image, rect)

    def draw_toggle(self, name, rect):
        active = (
            (name == "DAY" and not self.is_night) or
            (name == "NIGHT" and self.is_night) or
            (name == "RAIN" and self.is_rain)
        )

        color = (100,200,100) if active else (200,200,200)
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, (0,0,0), rect, 2, border_radius=8)
        txt = self.toggle_font.render(name, True, (0,0,0))
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    # =====================================================
    def run(self):
        last_time = time.time()

        while self.running:
            dt = time.time() - last_time
            last_time = time.time()
            self.light_timer += dt

            car_state = self.car_light_state()
            ped_state = self.ped_light_state()

            self.update_vehicles(dt, car_state)

            #green ped timer
            if ped_state == "GREEN":
                if not self.green_timer_running:
                    self.green_timer_running = True
                    self.green_timer = self.GREEN_TIMER_START
                else:
                    self.green_timer -= dt
                    if self.green_timer <= 0:
                        self.green_timer = 0
                        self.game_over = True
                        self.game_over_msg = "Time's up during GREEN light!"
                        self.show_retry = True
                        self.gameover_sound.play()
            else:
                self.green_timer_running = False

            # -------- EVENTS --------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    for name, rect in self.toggle_rects.items():
                        if rect.collidepoint((mx,my)):
                            self.click_sound.play()
                            if name == "DAY": self.is_night = False
                            if name == "NIGHT": self.is_night = True
                            if name == "RAIN":
                                self.is_rain = not self.is_rain
                                self.rain_sound.play(-1) if self.is_rain else self.rain_sound.stop()
                            

                    if self.game_over and self.retry_rect.collidepoint((mx,my)):
                        self.reset_all()
                        self.click_sound.play()

                    if self.success and self.next_rect.collidepoint((mx,my)):
                        self.click_sound.play()
                        self.running = False

                    if self.phone_active:
                        if self.answer_rect.collidepoint((mx,my)):
                            self.phone_sound.stop()
                            self.game_over = True
                            self.game_over_msg = "You answered the phone while crossing!"
                            self.show_retry = True
                            self.gameover_sound.play()
                        if self.decline_rect.collidepoint((mx,my)):
                            self.phone_active = False
                            self.phone_sound.stop()

            # -------- PLAYER MOVE --------
            if not self.game_over and not self.success and not self.phone_active:
                mouse = pygame.mouse.get_pressed()
                if mouse[0]:
                    mx, my = pygame.mouse.get_pos()
                    if self.up_rect.collidepoint(mx,my):
                        if self.ped_light_state() == "RED":
                            self.game_over = True
                            self.game_over_msg = "You moved on RED pedestrian light!"
                            self.show_retry = True
                            self.gameover_sound.play()
                        else:
                            self.player_y -= self.PLAYER_SPEED * dt * 60
                    if self.down_rect.collidepoint(mx,my):
                        self.player_y += self.PLAYER_SPEED * dt * 60

            # -------- PHONE EVENT --------
            on_crossing = (
                self.CROSSING_X <= self.player_x <= self.CROSSING_X + self.CROSSING_W and
                self.CROSSING_START_Y <= self.player_y <= self.CROSSING_END_Y
            )

            if on_crossing and not self.phone_triggered:
                self.phone_active = True
                self.phone_triggered = True
                self.phone_timer = 0.0
                self.phone_sound.play(-1)

            if self.phone_active:
                self.phone_timer += dt
                if self.phone_timer >= self.phone_duration:
                    self.phone_sound.stop()
                    self.game_over = True
                    self.game_over_msg = "You failed to decline the phone!"
                    self.show_retry = True
                    self.gameover_sound.play()

            # -------- RAIN --------
            if self.is_rain:
                self.spawn_rain()
                self.update_rain()

            # -------- VEHICLES --------
            for v in self.vehicles:
                if self.car_light_state() != "RED":
                    v["x"] += v["dir"] * v["speed"] * dt * 60
                if v["dir"] == 1 and v["x"] > self.WIDTH+300: v["x"] = -300
                if v["dir"] == -1 and v["x"] < -300: v["x"] = self.WIDTH+300

            # -------- SUCCESS --------
            if self.player_y <= self.FINISH_Y and not self.game_over:
                if not self.success:
                    self.success = True

                    self.traffic_sound.fadeout(1000)

                    self.success_sound.play(0, fade_ms=500)

            # -------- DRAW --------
            self.screen.blit(self.background,(0,0))

            for v in self.vehicles:
                img = self.car_img if v["dir"] == 1 else pygame.transform.flip(self.car_img, True, False)
                self.screen.blit(img,(v["x"],v["y"]))

            self.screen.blit(self.player_img,(self.player_x,self.player_y))
            self.draw_hoverable_button(self.up_rect,self.up_img)
            self.draw_hoverable_button(self.down_rect,self.down_img)

            if self.car_light_state()=="RED": self.screen.blit(self.red_light,(180,-80))
            elif self.car_light_state()=="YELLOW": self.screen.blit(self.yellow_light,(180,-80))
            else: self.screen.blit(self.green_light,(180,-80))

            ped = self.ped_green if self.ped_light_state()=="GREEN" else \
                  self.ped_yellow if self.ped_light_state()=="YELLOW" else self.ped_red
            self.screen.blit(ped,(285,75))

            if ped_state == "GREEN":
                timer_text = self.font_small.render(
                    f"Time: {int(self.green_timer)}",
                    True, 
                    (255, 255, 255)
                )
                self.screen.blit(timer_text, (self.WIDTH - 130, 20))
            
            car_text = self.font_small.render(
                f"Car Light: {car_state}",
                True,
                (255, 255, 255)
            )
            ped_text = self.font_small.render(
                f"Pedestrian Light: {ped_state}",
                True,
                (255, 255, 255)
            )

            self.screen.blit(car_text, (30, 70))
            self.screen.blit(ped_text, (30, 94))

            for n,r in self.toggle_rects.items():
                self.draw_toggle(n,r)

            if self.is_rain:
                self.draw_rain()

            if self.is_night:
                night = pygame.Surface((self.WIDTH,self.HEIGHT),pygame.SRCALPHA)
                night.fill((0,0,0,140))
                self.screen.blit(night,(0,0))

           # ================= PHONE UI =================
            if self.phone_active:
                overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                self.screen.blit(overlay, (0, 0))

                info = self.font_small.render(
                    "Phone is ringing!",
                    True,
                    (255, 255, 255)
                )
                self.screen.blit(
                    info,
                    info.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 40))
                )

                self.draw_hoverable_button(self.answer_rect, self.answer_img, 1.15)
                self.draw_hoverable_button(self.decline_rect, self.decline_img, 1.15)

            if self.game_over:
                self.draw_game_over()

            if self.success:
                self.draw_success()
            

            pygame.display.flip()
            self.clock.tick(60)

    # =====================================================
    def draw_game_over(self):
        s = pygame.Surface((self.WIDTH,self.HEIGHT),pygame.SRCALPHA)
        s.fill((0,0,0,200)); self.screen.blit(s,(0,0))
        txt = self.font_big.render("GAME OVER",True,(255,40,40))
        self.screen.blit(txt,txt.get_rect(center=(self.WIDTH//2,self.HEIGHT//2-80)))
        msg = self.font_small.render(self.game_over_msg,True,(255,255,255))
        self.screen.blit(msg,msg.get_rect(center=(self.WIDTH//2,self.HEIGHT//2-20)))
        self.draw_hoverable_button(self.retry_rect,self.retry_img)

    def draw_success(self):
        s = pygame.Surface((self.WIDTH,self.HEIGHT),pygame.SRCALPHA)
        s.fill((0,0,0,120)); self.screen.blit(s,(0,0))
        win = self.font_big.render("SUCCESS!",True,(0,230,40))
        self.screen.blit(win,win.get_rect(center=(self.WIDTH//2,self.HEIGHT//2)))
        self.draw_hoverable_button(self.next_rect,self.next_img,1.01)


# ================= RUN =================
if __name__ == "__main__":
    screen = pygame.display.set_mode((900,600))
    pygame.display.set_caption("Pedestrian Simulation")
    SimulationScene(screen).run()




