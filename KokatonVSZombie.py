import pygame
import sys
import os
import random

# Pygameの初期化
pygame.init()

# 画面サイズとマス目サイズの設定
GRID_ROWS = 5  # マスの行数
GRID_COLUMNS = 9  # マスの列数
GRID_SIZE = 90  # 1つのマスのサイズ（変更）
INFO_AREA_HEIGHT = 80  # 上部の情報エリアの高さ
GRID_OFFSET_X = 150  # マス目を右にずらすオフセット
SCREEN_WIDTH = GRID_COLUMNS * GRID_SIZE + GRID_OFFSET_X + 200  # 画面の幅を広げる
SCREEN_HEIGHT = GRID_ROWS * GRID_SIZE + INFO_AREA_HEIGHT  # 画面の高さ

# 色の定義 (RGB形式)
GREEN = (0, 128, 0)  # 背景の緑色
WHITE = (255, 255, 255)  # マス目の線の色
BLACK = (0, 0, 0)  # テキストの色
GRAY = (200, 200, 200)  # 情報エリアの背景色
RED = (255, 0, 0)  # 敵ゾンビの色
BLUE = (0, 0, 255)  # 弾の色
HP_GREEN = (0, 255, 0)  # HPバーの色

# 画面の作成
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plants vs Zombies 風ゲーム")

# フォントの設定
font = pygame.font.Font(None, 36)

# 画像の読み込みと反転
current_path = os.path.dirname(__file__)  # カレントディレクトリ
plant_image = pygame.image.load(os.path.join(current_path, "fig", "7.png"))  # 植物画像
plant_image = pygame.transform.flip(plant_image, True, False)
plant_image = pygame.transform.scale(plant_image, (50, 75))  # サイズ調整

# moneyの初期値と回復設定
money = 100
money_increase_interval = 2000  # moneyが増える間隔（ミリ秒）
money_increase_amount = 10  # 増える金額
last_money_update = pygame.time.get_ticks()  # 最後にmoneyを増やした時間

# 弾の攻撃力
BULLET_DAMAGE = 5
BULLET_SPEED = 5

# ゾンビの出現管理
zombie_spawn_interval = 5000  # 5秒ごとにゾンビを出現
last_zombie_spawn = pygame.time.get_ticks()

# HPバーを描画する関数
def draw_hp_bar(surface, rect, hp, max_hp):
    """HPバーを描画"""
    bar_width = rect.width
    bar_height = 6
    hp_ratio = hp / max_hp
    hp_width = int(bar_width * hp_ratio)

    # HPバーの背景（赤）
    pygame.draw.rect(surface, RED, (rect.x, rect.y - bar_height - 2, bar_width, bar_height))
    # 現在のHP（緑）
    if hp > 0:
        pygame.draw.rect(surface, HP_GREEN, (rect.x, rect.y - bar_height - 2, hp_width, bar_height))

# ゾンビクラスの定義
class Zombie:
    """ゾンビの設定"""
    def __init__(self, x, y, speed, hp, zombie_image_path):
        self.rect = pygame.Rect(x, y, 50, 75)
        self.image = pygame.image.load(os.path.join(current_path, "fig", zombie_image_path))  # ゾンビ画像
        self.image = pygame.transform.scale(self.image, (75, 95))
        self.image = pygame.transform.flip(self.image, True, False)
        self.speed = speed
        self.initial_speed = speed  # 元の速度を保存
        self.hp = hp  # ゾンビのHP
        self.max_hp = hp
        self.alive = True
        self.attacking = False  # 攻撃中フラグ

    def move(self):
        if self.alive and not self.attacking:  # 攻撃中でない場合に移動
            self.rect.x -= self.speed
        else:  # 攻撃中は速度を保持するが移動しない
            self.speed = 0

    def take_damage(self, damage):
        """ダメージを受ける"""
        self.hp -= damage
        if self.hp <= 0: 
            self.alive = False
            self.attacking = False  # 攻撃状態を解除

    def reset_speed(self):
        """速度を元に戻す"""
        self.speed = self.initial_speed

    def draw(self, surface):
        if self.alive:
            surface.blit(self.image, self.rect.topleft)
            draw_hp_bar(surface, self.rect, self.hp, self.max_hp)

    def is_off_screen(self):
        """ゾンビが左端を通過したかを判定"""
        return self.rect.x < GRID_OFFSET_X
    
# 植物クラスの定義
class Plant:
    def __init__(self, x, y, hp):
        self.rect = pygame.Rect(x, y, 50, 75)
        self.hp = hp  # 植物のHP
        self.max_hp = hp
        self.alive = True
        self.last_shot_time = pygame.time.get_ticks()

    def take_damage(self, damage):
        """ダメージを受ける"""
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False

    def shoot(self, zombies):
        """2秒間隔で弾を発射"""
        for zombie in zombies:
            if zombie.alive and zombie.rect.y == self.rect.y:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_shot_time >= 2000:  # 2秒間隔
                    self.last_shot_time = current_time
                    return Bullet(self.rect.right, self.rect.centery)
        return None

    def draw(self, surface):
        if self.alive:
            surface.blit(plant_image, self.rect.topleft)
            draw_hp_bar(surface, self.rect, self.hp, self.max_hp)

# 弾クラスの定義
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 10)

    def move(self):
        """弾を右方向に移動"""
        self.rect.x += BULLET_SPEED

    def draw(self, surface):
        pygame.draw.circle(surface, BLUE, self.rect.center, 5)

# テキストを描画する関数
def draw_text(surface, text, x, y, color):
    rendered_text = font.render(text, True, color)
    surface.blit(rendered_text, (x, y))

# マス目を描画する関数
def draw_grid(surface, rows, columns, grid_size, offset_x, offset_y):
    for x in range(0, columns * grid_size + 1, grid_size):  # 右端の線を含める
        pygame.draw.line(surface, WHITE, (x + offset_x, offset_y), (x + offset_x, offset_y + rows * grid_size))
    for y in range(offset_y, offset_y + rows * grid_size + 1, grid_size):  # 下端の線を含める
        pygame.draw.line(surface, WHITE, (offset_x, y), (offset_x + columns * grid_size, y))

# 情報エリアを描画する関数
def draw_info_area(surface, width, height, money, plant_image):
    # 情報エリア背景
    pygame.draw.rect(surface, GRAY, (0, 0, width, height))
    # money表示（左上）
    draw_text(surface, f"money: {money}", 20, 20, BLACK)
    # SETエリア（moneyの右側に配置）
    set_area_x = 160  # moneyの隣に配置
    draw_text(surface, "SET", set_area_x, 20, BLACK)
    surface.blit(plant_image, (set_area_x + 50, 5))  # SETエリアに植物アイコンを表示

# メインのゲームループ
def main():
    global money, last_money_update, last_zombie_spawn
    clock = pygame.time.Clock()

    # ゾンビと植物のリスト
    zombies = []
    plants = []
    bullets = []

    # 植物のドラッグ管理
    dragging = False
    dragging_plant_rect = plant_image.get_rect()

    # ゲームループ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                set_area_x = 150
                set_area_rect = pygame.Rect(set_area_x + 50, 13, plant_image.get_width(), plant_image.get_height())
                if set_area_rect.collidepoint(event.pos):
                    dragging = True
                    dragging_plant_rect.topleft = event.pos

            elif event.type == pygame.MOUSEMOTION and dragging:
                dragging_plant_rect.center = event.pos

            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                dragging = False
                mouse_x, mouse_y = event.pos
                if mouse_y > INFO_AREA_HEIGHT and mouse_x > GRID_OFFSET_X and money >= 50:
                    grid_x = ((mouse_x - GRID_OFFSET_X) // GRID_SIZE) * GRID_SIZE + GRID_OFFSET_X
                    grid_y = ((mouse_y - INFO_AREA_HEIGHT) // GRID_SIZE) * GRID_SIZE + INFO_AREA_HEIGHT
                    plants.append(Plant(grid_x, grid_y, hp=100))
                    money -= 50

        # 時間経過でmoneyを増やす
        current_time = pygame.time.get_ticks()
        if current_time - last_money_update >= money_increase_interval:
            money += money_increase_amount
            last_money_update = current_time

        # ゾンビを定期的に出現
        if current_time - last_zombie_spawn >= zombie_spawn_interval:
            random_zombie = random.randint(0, 100)
            random_row = random.randint(0, GRID_ROWS - 1)
            if random_zombie <= 50:
                #50%で通常ゾンビ
                zombies.append(Zombie(SCREEN_WIDTH - 50, INFO_AREA_HEIGHT + random_row * GRID_SIZE, speed=2, hp=30, zombie_image_path="zombie_image_2.png"))
            elif 51 <= random_zombie <= 75:  
                #25%で足早+耐久低ゾンビ
                zombies.append(Zombie(SCREEN_WIDTH - 50, INFO_AREA_HEIGHT + random_row * GRID_SIZE, speed=4, hp=10, zombie_image_path="zombie_image_1.png"))
            elif 76 <= random_zombie <= 100:
                #25%で足遅+耐久高ゾンビ
                zombies.append(Zombie(SCREEN_WIDTH - 50, INFO_AREA_HEIGHT + random_row * GRID_SIZE, speed=1, hp=60, zombie_image_path="zombie_image_3.png"))
            last_zombie_spawn = current_time

        # 植物が弾を発射
        for plant in plants:
            if plant.alive:
                bullet = plant.shoot(zombies)
                if bullet:
                    bullets.append(bullet)

        # 弾の移動と衝突判定
        for bullet in bullets[:]:
            bullet.move()
            for zombie in zombies:
                if zombie.alive and bullet.rect.colliderect(zombie.rect):
                    zombie.take_damage(BULLET_DAMAGE)
                    bullets.remove(bullet)
                    break
            if bullet.rect.x > SCREEN_WIDTH:
                bullets.remove(bullet)

        # 背景の描画
        screen.fill(GREEN)
        draw_info_area(screen, SCREEN_WIDTH, INFO_AREA_HEIGHT, money, plant_image)
        draw_grid(screen, GRID_ROWS, GRID_COLUMNS, GRID_SIZE, GRID_OFFSET_X, INFO_AREA_HEIGHT)

        # ゾンビと植物の衝突判定
        for zombie in zombies:
            zombie.attacking = False  # 初期化：毎ループでリセット
            for plant in plants:
                if zombie.alive and plant.alive and zombie.rect.colliderect(plant.rect):
                    zombie.attacking = True  # 衝突中
                    plant.take_damage(0.3)  # 植物に継続的ダメージ
                    if plant.hp <= 0:  # 植物が倒れた場合
                        plant.alive = False  # 植物を無効化
                        zombie.attacking = False  # ゾンビは再び移動可能
                        zombie.reset_speed()
        for zombie in zombies[:]:
            if zombie.alive:
                zombie.move()
                zombie.draw(screen)

        # 植物の描画
        for plant in plants[:]:
            if plant.alive:
                plant.draw(screen)

        # 弾の描画
        for bullet in bullets:
            bullet.draw(screen)

        # ドラッグ中の植物の描画
        if dragging:
            screen.blit(plant_image, dragging_plant_rect.topleft)

        # ゲームオーバー判定
        for zombie in zombies:
            if zombie.is_off_screen():
                draw_text(screen, "GAME OVER", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, BLACK)
                pygame.display.update()
                pygame.time.wait(3000)
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()