import peasy.PeasyCam;

PeasyCam cam;
PointsObj po;

void setup() {
  size(1024, 768, P3D);
  cam = new PeasyCam(this, 400);
  po = new PointsObj("test.obj");
}

void draw() {
  background(0);
  pushMatrix();
  rotateX(radians(180));
  strokeWeight(0.02);
  scale(100, 100, 100);
  po.draw();
  popMatrix();

  surface.setTitle("" + frameRate);
}
