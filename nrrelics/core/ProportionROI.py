from dataclasses import dataclass

from mss.models import Monitor


#归一化后表示百分比 非归一化表示绝对位置
@dataclass
class ProportionROI:

    x1 : float
    y1 : float
    x2 : float
    y2 : float

    def getROI(self,monitor : Monitor) -> dict[str,int]:
        if self.x1 > 1 and self.y1 > 1 and self.x2 > 1 and self.y2 > 1:
            return {
                "top": int(self.y1),
                "left": int(self.x1),
                "width": int(self.x2 - self.x1),
                "height": int(self.y2 - self.y1)
            }
        w, h = monitor["width"], monitor["height"]
        return {
            "top": monitor["top"] + int(h * self.y1),
            "left": monitor["left"] + int(w * self.x1),
            "width": int(w * (self.x2 - self.x1)),
            "height": int(h * (self.y2 - self.y1))
        }

    def getCenter(self, monitor : Monitor) -> tuple[int, int]:
        px = (self.x1 + self.x2)/2
        py = (self.y1 + self.y2)/2
        if px > 1 and py > 1:
            return int(px), int(py)
        w, h = monitor["width"], monitor["height"]
        return int(w*px), int(h*py)

    def to_dict(self) -> dict:
        return dict(self.__dict__)