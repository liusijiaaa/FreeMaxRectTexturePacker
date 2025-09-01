# maxrects.py
from typing import List, Optional, Tuple

class MaxRectsPacker:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # 初始时整个区域为空闲
        self.free_rects: List[Rect] = [Rect(0, 0, width, height)]

    def insert(self, w: int, h: int) -> Optional[Tuple[int, int]]:
        """尝试插入 w x h 的矩形，返回 (x, y)，失败返回 None"""
        best_rect = None
        best_score = float('inf')

        # 找到最适合的空闲矩形（最小面积浪费）
        for rect in self.free_rects:
            if rect.w >= w and rect.h >= h:
                score = rect.w * rect.h - w * h  # 剩余面积越小越好
                if score < best_score:
                    best_score = score
                    best_rect = rect

        if not best_rect:
            return None  # 无法插入

        x, y = best_rect.x, best_rect.y

        # 分割剩余空间（Guillotine 切割）
        new_free = []

        # 右侧区域
        if best_rect.w > w:
            new_free.append(Rect(x + w, y, best_rect.w - w, h))
        # 下方区域
        if best_rect.h > h:
            new_free.append(Rect(x, y + h, best_rect.w, best_rect.h - h))

        # 移除已使用的矩形
        self.free_rects.remove(best_rect)

        # 添加新空闲区域
        self.free_rects.extend(new_free)

        # 合并重叠或相邻的空闲矩形（关键！减少碎片）
        self._merge_free_rects()

        return x, y

    def _merge_free_rects(self):
        """合并可以合并的空闲矩形（水平或垂直）"""
        i = 0
        while i < len(self.free_rects):
            j = i + 1
            merged = False
            while j < len(self.free_rects):
                if self.free_rects[i].can_merge(self.free_rects[j]):
                    self.free_rects[i] = self.free_rects[i].merge(self.free_rects[j])
                    self.free_rects.pop(j)
                    merged = True
                    break
                j += 1
            if not merged:
                i += 1

# ======================
# 辅助类：矩形
# ======================
class Rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

    def can_merge(self, other: 'Rect') -> bool:
        """判断两个矩形是否可以合并（必须边对齐且共线）"""
        # 水平合并：同一行，y 相同，高度相同
        if self.y == other.y and self.h == other.h:
            if self.x + self.w == other.x or other.x + other.w == self.x:
                return True
        # 垂直合并：同一列，x 相同，宽度相同
        if self.x == other.x and self.w == other.w:
            if self.y + self.h == other.y or other.y + other.h == self.y:
                return True
        return False

    def merge(self, other: 'Rect') -> 'Rect':
        """合并两个矩形"""
        if self.y == other.y and self.h == other.h:  # 水平合并
            x = min(self.x, other.x)
            w = self.w + other.w
            return Rect(x, self.y, w, self.h)
        if self.x == other.x and self.w == other.w:  # 垂直合并
            y = min(self.y, other.y)
            h = self.h + other.h
            return Rect(self.x, y, self.w, h)
        return self  # 不应发生

    def __repr__(self):
        return f"Rect({self.x},{self.y},{self.w},{self.h})"

def align_to_multiple(value, multiple=4):
    """将值向上对齐到指定的倍数"""
    return ((value + multiple - 1) // multiple) * multiple