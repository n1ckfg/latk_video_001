import peasy.PeasyCam;

PeasyCam cam;
PointsObj po;

FloatToPixel f2p;
int maxColor = 255 * 255 * 255;
GameState gs;

void setup() {
  size(1024, 1024, P3D);
  gs = GameState.OBJ;

  cam = new PeasyCam(this, 400);
  po = new PointsObj("test.obj");
  
  f2p = new FloatToPixel(po);
}

void draw() {
  background(0);
  
  switch (gs) {
    case OBJ:
      lights();
      pushMatrix();
      strokeWeight(0.02);
      scale(100, 100, 100);
      rotateX(radians(180));
      po.draw();
      popMatrix();
      break;
    case F2P:
      f2p.draw();
      break;
    case P2F:
      break;
  }
  
  surface.setTitle("" + frameRate);
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
