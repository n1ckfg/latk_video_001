import peasy.PeasyCam;

PeasyCam cam;
PShape pod;
PointsObj podObj;

FloatToPixel f2p;
int maxColor = 255 * 255 * 255;
GameState gs;

void setup() {
  size(1024, 1024, P3D);
  gs = GameState.OBJ;

  cam = new PeasyCam(this, 400);
  pod = loadShape("test.obj");
  podObj = new PointsObj(pod);
  
  f2p = new FloatToPixel();
}

void draw() {
  background(0);
  
  switch (gs) {
    case OBJ:
      lights();
      pushMatrix();
      //translate(width/2, height/2, -500);
      //scale(1000, 1000, 1000);
      rotateX(radians(180));
      rotateY(radians(90));
      shape(pod, 0, 0);
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
