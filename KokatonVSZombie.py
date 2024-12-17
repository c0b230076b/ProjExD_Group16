import pygame
import sys
import os

# Pygameの初期化
pygame.init()

# 画面サイズとマス目サイズの設定
SCREEN_WIDTH = 800  # 画面の幅
SCREEN_HEIGHT = 600  # 画面の高さ
GRID_SIZE = 80  # 1つのマスのサイズ
INFO_AREA_HEIGHT = 80  # 上部の情報エリアの高さ

# 色の定義 (RGB形式)
GREEN = (0, 128, 0)  # 背景の緑色
WHITE = (255, 255, 255)  # マス目の線の色
BLACK = (0, 0, 0)  # テキストの色
GRAY = (200, 200, 200)  # 情報エリアの背景色

# 画面の作成
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plants vs Zombies 風ゲーム")

# フォントの設定
font = pygame.font.Font(None, 36)

# 画像の読み込みと反転
current_path = os.path.dirname(__file__)  # カレントディレクトリ
plant_image = pygame.image.load(os.path.join(current_path, "fig", "7.png"))  # プレイヤー側の画像
plant_image = pygame.transform.flip(plant_image, True, False)  # 左右反転
plant_image = pygame.transform.scale(plant_image, (48, 67))  # 画像サイズを調整

# SETエリアの座標
SET_AREA_X = 250
SET_AREA_Y = 20

# テキストを描画する関数
def draw_text(surface, text, x, y, color):
    rendered_text = font.render(text, True, color)
    surface.blit(rendered_text, (x, y))

# マス目を描画する関数
def draw_grid(surface, width, height, grid_size, offset_y):
    for x in range(0, width, grid_size):
        pygame.draw.line(surface, WHITE, (x, offset_y), (x, height))
    for y in range(offset_y, height, grid_size):
        pygame.draw.line(surface, WHITE, (0, y), (width, y))

# 情報エリアを描画する関数
def draw_info_area(surface, width, height, plant_icon):
    pygame.draw.rect(surface, GRAY, (0, 0, width, height))
    draw_text(surface, "money: 0", 20, 20, BLACK)
    draw_text(surface, "SET", 200, 20, BLACK)
    surface.blit(plant_icon, (SET_AREA_X, SET_AREA_Y))  # SETエリアに植物を描画

# メインのゲームループ
def main():
    clock = pygame.time.Clock()

    # 植物（キャラクタ）のドラッグ管理
    dragging = False
    plant_drag_rect = plant_image.get_rect(topleft=(SET_AREA_X, SET_AREA_Y))  # ドラッグするキャラクタの初期位置
    plants = []  # 配置された植物を格納

    # ゲームループ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ドラッグ開始
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if plant_drag_rect.collidepoint(event.pos):  # SETエリアのキャラクタをクリック
                    dragging = True

            # ドラッグ中の処理
            elif event.type == pygame.MOUSEMOTION and dragging:
                plant_drag_rect.center = event.pos  # マウスに追従

            # ドラッグ終了（キャラクタをマス目に配置）
            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                dragging = False
                mouse_x, mouse_y = event.pos
                if mouse_y > INFO_AREA_HEIGHT:  # 情報エリア外で配置
                    grid_x = (mouse_x // GRID_SIZE) * GRID_SIZE
                    grid_y = (mouse_y // GRID_SIZE) * GRID_SIZE
                    plants.append((grid_x, grid_y))  # 植物の位置を記録

                # SETエリアにアイコンを戻す
                plant_drag_rect.topleft = (SET_AREA_X, SET_AREA_Y)

        # 背景の描画
        screen.fill(GREEN)

        # 情報エリアとSETエリアの描画
        draw_info_area(screen, SCREEN_WIDTH, INFO_AREA_HEIGHT, plant_image)

        # マス目の描画
        draw_grid(screen, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, INFO_AREA_HEIGHT)

        # 配置された植物の描画
        for x, y in plants:
            screen.blit(plant_image, (x, y))

        # ドラッグ中のキャラクタの描画
        if dragging:
            screen.blit(plant_image, plant_drag_rect.topleft)

        # 画面の更新
        pygame.display.update()
        clock.tick(60)

# メイン関数の実行
if __name__ == "__main__":
    main()
