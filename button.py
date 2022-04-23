from funcs import *


class Button:
    def __init__(self, pos, size, txt='', img=None, col=WHITE):
        self.pos = pos
        self.col = col
        self.text = txt
        self.img = img
        self.original_size = self.size = size
        if img:
            # create smaller and bigger copies of an image for highlighting
            img_w, img_h = self.img.get_rect().size
            scale = self.size / img_w
            self.smaller_img = pg.transform.scale(self.img, (int(img_w * scale), int(img_h * scale)))
            scale = (self.size + 5) / img_w
            self.bigger_img = pg.transform.scale(self.img, (int(img_w * scale), int(img_h * scale)))
        if txt:
            self.rect = text_rect(txt, size)
        elif img:
            self.rect = self.smaller_img.get_rect()

    def params(self):
        """Returns the top left corner point"""
        return (self.pos[0] + self.rect.left - self.rect.width / 2,
                self.pos[1] + self.rect.top - self.rect.height / 2,
                self.rect.width,
                self.rect.height)

    def highlighted(self):
        """Is called if the mouse is above the button, changes the size of the mouse"""
        x, y, w, h = self.params()
        pos = pg.mouse.get_pos()
        if in_rect(Point(pos), x, y, w, h):
            self.size = self.original_size + 5
        else:
            self.size = self.original_size

    def triggered(self, channel=None, sound=None, playing=False):
        """Returns True if the button is pressed"""
        x, y, w, h = self.params()
        pos = pg.mouse.get_pos()
        if in_rect(Point(pos), x, y, w, h) and channel and sound and playing:
            channel.play(sound)
        return in_rect(Point(pos), x, y, w, h)

    def img_update(self):
        if self.img:
            if self.size > self.original_size:
                self.img = self.bigger_img
            else:
                self.img = self.smaller_img

    def show(self, surface):
        if self.text:
            text_out(surface, self.text, self.size, self.col, self.pos)
        elif self.img:
            self.img_update()
            img_w, img_h = self.img.get_rect().size
            surface.blit(self.img, (self.pos[0] - img_w / 2, self.pos[1] - img_h / 2))
