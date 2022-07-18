
FloatToPixel f2p;
int maxColor = 255 * 255 * 255;

void setup() {
  size(1024, 1024);
  f2p = new FloatToPixel();
}

void draw() {
  background(0);
  f2p.draw();
}

color getColorFromInt(int val) {
  int rMask = 255 << 16;
  int gMask = 255 << 8;
  int bMask = 255;
  
  int r = (val & rMask) >> 16;
  int g = (val & gMask) >> 8;
  int b = val & bMask;

  return color(r, g, b);
}
