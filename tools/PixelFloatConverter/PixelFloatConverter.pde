import peasy.PeasyCam;

PeasyCam cam;
PointsObj po;

FloatToPixel f2p;
PixelToFloat p2f;
int maxColor = 255 * 255 * 255;
GameState gs;

void setup() {
  size(1024, 1024, P3D);
  gs = GameState.OBJ;

  cam = new PeasyCam(this, 400);
  po = new PointsObj("test.obj");
  
  f2p = new FloatToPixel(po);
  //p2f = new PixelToFloat(f2p);
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
