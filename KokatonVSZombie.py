import pygame
import sys
import os
import random

# Pygameの初期化
pygame.init()

# 画面サイズとマス目サイズの設定
GRID_ROWS = 5  # マスの行数
GRID_COLUMNS = 9  # マスの列数
GRID_SIZE = 80  # 1つのマスのサイズ
INFO_AREA_HEIGHT = 80  # 上部の情報エリアの高さ
SCREEN_WIDTH = GRID_COLUMNS * GRID_SIZE + 200  # 画面の幅を広げる
SCREEN_HEIGHT = GRID_ROWS * GRID_SIZE + INFO_AREA_HEIGHT  # 画面の高さ

# 色の定義 (RGB形式)
GREEN = (0, 128, 0)  # 背景の緑色
WHITE = (255, 255, 255)  # マス目の線の色
BLACK = (0, 0, 0)  # テキストの色
GRAY = (200, 200, 200)  # 情報エリアの背景色
RED = (255, 0, 0)  # 敵ゾンビの色

# 画面の作成
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plants vs Zombies 風ゲーム")

# フォントの設定
font = pygame.font.Font(None, 36)

# 画像の読み込みと反転
current_path = os.path.dirname(__file__)  # カレントディレクトリ
plant_image = pygame.image.load(os.path.join(current_path, "fig", "7.png"))  # 植物画像
plant_image = pygame.transform.flip(plant_image, True, False)
plant_image = pygame.transform.scale(plant_image, (48, 67))

# SETエリアの座標
SET_AREA_X = 250
SET_AREA_Y = 20

# moneyの初期値と回復設定
money = 100
money_increase_interval = 2000  # moneyが増える間隔（ミリ秒）
money_increase_amount = 10  # 増える金額
last_money_update = pygame.time.get_ticks()  # 最後にmoneyを増やした時間

# ゾンビの出現管理
zombie_spawn_interval = 5000  # 5秒ごとにゾンビを出現
last_zombie_spawn = pygame.time.get_ticks()

# ゾンビクラスの定義
class Zombie:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, 48, 67)
        self.speed = speed
        self.alive = True

    def move(self):
        if self.alive:
            self.rect.x -= self.speed

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, RED, self.rect)

    def is_off_screen(self):
        """ゾンビが画面左端を通過したかを判定"""
        return self.rect.x < 0

# テキストを描画する関数
def draw_text(surface, text, x, y, color):
    rendered_text = font.render(text, True, color)
    surface.blit(rendered_text, (x, y))

# マス目を描画する関数
def draw_grid(surface, rows, columns, grid_size, offset_y):
    for x in range(0, columns * grid_size, grid_size):
        pygame.draw.line(surface, WHITE, (x, offset_y), (x, offset_y + rows * grid_size))
    for y in range(offset_y, offset_y + rows * grid_size, grid_size):
        pygame.draw.line(surface, WHITE, (0, y), (columns * grid_size, y))

# 情報エリアを描画する関数
def draw_info_area(surface, width, height, plant_icon, money):
    pygame.draw.rect(surface, GRAY, (0, 0, width, height))
    draw_text(surface, f"money: {money}", 20, 20, BLACK)
    draw_text(surface, "SET", 200, 20, BLACK)
    surface.blit(plant_icon, (SET_AREA_X, SET_AREA_Y))

# メインのゲームループ
def main():
    global money, last_money_update, last_zombie_spawn
    clock = pygame.time.Clock()

    # ゾンビリスト
    zombies = []

    # 植物のドラッグ管理
    dragging = False
    plant_drag_rect = plant_image.get_rect(topleft=(SET_AREA_X, SET_AREA_Y))
    plants = []  # 配置された植物のリスト

    # ゲームループ
    while True:
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ドラッグ開始
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if plant_drag_rect.collidepoint(event.pos):
                    dragging = True

            # ドラッグ中
            elif event.type == pygame.MOUSEMOTION and dragging:
                plant_drag_rect.center = event.pos

            # ドラッグ終了（植物配置）
            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                dragging = False
                mouse_x, mouse_y = event.pos
                if mouse_y > INFO_AREA_HEIGHT and money >= 50:  # 植物設置にmoneyが必要
                    grid_x = (mouse_x // GRID_SIZE) * GRID_SIZE
                    grid_y = ((mouse_y - INFO_AREA_HEIGHT) // GRID_SIZE) * GRID_SIZE + INFO_AREA_HEIGHT
                    plants.append((grid_x, grid_y))
                    money -= 50  # 植物配置でお金を消費
                plant_drag_rect.topleft = (SET_AREA_X, SET_AREA_Y)

        # 時間経過でmoneyを増やす
        current_time = pygame.time.get_ticks()
        if current_time - last_money_update >= money_increase_interval:
            money += money_increase_amount
            last_money_update = current_time

        # ゾンビを定期的に出現させる
        if current_time - last_zombie_spawn >= zombie_spawn_interval:
            random_row = random.randint(0, GRID_ROWS - 1)
            zombies.append(Zombie(SCREEN_WIDTH - 50, INFO_AREA_HEIGHT + random_row * GRID_SIZE, 1))  # ゾンビのスピードは遅め
            last_zombie_spawn = current_time

        # 背景の描画
        screen.fill(GREEN)
        draw_info_area(screen, SCREEN_WIDTH, INFO_AREA_HEIGHT, plant_image, money)
        draw_grid(screen, GRID_ROWS, GRID_COLUMNS, GRID_SIZE, INFO_AREA_HEIGHT)

        # ゾンビの動きと描画
        for zombie in zombies:
            zombie.move()
            zombie.draw(screen)

        # ゲームオーバー判定
        for zombie in zombies:
            if zombie.is_off_screen():
                draw_text(screen, "GAME OVER", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, BLACK)
                pygame.display.update()
                pygame.time.wait(3000)
                pygame.quit()
                sys.exit()

        # 配置された植物の描画
        for x, y in plants:
            screen.blit(plant_image, (x, y))

        # ドラッグ中の植物の描画
        if dragging:
            screen.blit(plant_image, plant_drag_rect.topleft)

        # 画面の更新
        pygame.display.update()
        clock.tick(60)

# メイン関数の実行
if __name__ == "__main__":
    main()
