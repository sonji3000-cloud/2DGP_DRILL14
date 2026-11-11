from pico2d import get_canvas_width, load_image

import game_framework


PIXEL_PER_METER = 10.0 / 0.3
FLY_SPEED_KMPH = 32.0
FLY_SPEED_MPS = FLY_SPEED_KMPH * 1000.0 / 3600.0
FLY_SPEED_PPS = FLY_SPEED_MPS * PIXEL_PER_METER

BIRD_COUNT = 10
DISPLAY_WIDTH = 100.0
DISPLAY_HEIGHT = 90.0
SPRITE_SCALE = min(DISPLAY_WIDTH / 200.0, DISPLAY_HEIGHT / 180.0)
ANIMATION_PERIOD = 2.0

# 원본의 위쪽 기준: (크롭 x, 크롭 y, 너비, 높이, 몸체 기준 x, 몸체 기준 y).
# 눈 위치를 기준으로 몸체를 정렬하여 날개 모양과 무관하게 중심을 유지한다.
# 마지막 행의 빈 다섯 번째 칸은 포함하지 않는다.
FRAME_DATA = (
    (0, 0, 182, 168, 100, 105),
    (182, 0, 183, 168, 282, 105),
    (365, 0, 183, 168, 464, 103),
    (548, 0, 180, 168, 646, 100),
    (728, 0, 190, 168, 828, 97),
    (0, 168, 182, 178, 100, 266),
    (182, 168, 183, 178, 282, 265),
    (365, 168, 183, 178, 464, 266),
    (548, 168, 180, 178, 646, 266),
    (728, 168, 190, 178, 828, 268),
    (0, 346, 182, 160, 100, 441),
    (182, 346, 183, 160, 282, 444),
    (365, 346, 183, 160, 464, 445),
    (548, 346, 180, 160, 646, 445),
)
FRAME_COUNT = len(FRAME_DATA)


class Bird:
    image = None

    def __init__(self, index):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')

        self.x = 125.0 + 150.0 * index
        self.y = (420.0, 520.0, 470.0)[index % 3]
        self.direction = 1 if index % 2 == 0 else -1
        self.phase = ANIMATION_PERIOD * index / BIRD_COUNT

    def update(self):
        dt = game_framework.frame_time

        left = DISPLAY_WIDTH / 2.0
        right = get_canvas_width() - DISPLAY_WIDTH / 2.0
        span = right - left

        # 왕복 경로를 한 방향의 거리로 펼친 뒤 화면 안으로 접는다.
        # 큰 dt로 여러 경계를 지나도 초과 이동 거리를 버리지 않는다.
        distance = self.x - left
        if self.direction < 0:
            distance = 2.0 * span - distance
        distance = (distance + FLY_SPEED_PPS * dt) % (2.0 * span)

        if distance < span:
            self.x = left + distance
            self.direction = 1
        else:
            self.x = right - (distance - span)
            self.direction = -1

        self.phase = (self.phase + dt) % ANIMATION_PERIOD

    def draw(self):
        frame = int(self.phase * FRAME_COUNT / ANIMATION_PERIOD)
        clip_x, top, width, height, anchor_x, anchor_y = FRAME_DATA[frame]
        clip_y = self.image.h - top - height

        # 모든 프레임에 같은 배율을 쓰고 크롭 중심과 몸체 기준점의 차이를 보정한다.
        offset_x = (clip_x + width / 2.0 - anchor_x) * SPRITE_SCALE
        offset_y = (anchor_y - top - height / 2.0) * SPRITE_SCALE
        flip = '' if self.direction > 0 else 'h'
        self.image.clip_composite_draw(
            clip_x, clip_y, width, height,
            0, flip,
            self.x + self.direction * offset_x, self.y + offset_y,
            width * SPRITE_SCALE, height * SPRITE_SCALE,
        )
