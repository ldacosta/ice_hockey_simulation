from util.base import normalize_to


class World2CanvasConverter(object):

    MAX_WIDTH = 1280
    MAX_HEIGHT = 800

    X_MARGIN = 20
    Y_MARGIN = 20

    def __init__(self,
                 world_width: float, world_height: float):
        self.world_width = world_width
        self.world_height = world_height
        self.size_multiplier = int(min([self.MAX_HEIGHT/self.world_height, self.MAX_WIDTH/self.world_width]))
        self.screen_width = self.world_width * self.size_multiplier
        self.screen_height = self.world_height * self.size_multiplier


    def x_on_screen(self, x_wc: float) -> float:
        return self.X_MARGIN/2 + normalize_to(a_value=x_wc,
                                                        new_min=0.0, new_max=self.screen_width,
                                                        old_min=0.0, old_max=self.world_width)


    def y_on_screen(self, y_wc: float) -> float:
        return self.Y_MARGIN/2 + normalize_to(a_value=y_wc,
                                                        new_min=0.0, new_max=self.screen_height,
                                                        old_min=0.0, old_max=self.world_height)
