import peasy.PeasyCam;

PeasyCam cam;

PImage img, imgRgb, imgX, imgY, imgZ;
PShape ps;
int dim = 1024;
int hdim = dim/2;
int len = hdim * hdim;
float maxIntVal = 255 * 255 * 255;
float scaleVal = 200;
float strokeWeightVal = 1;

void setup() {
  size(1024, 1024, P3D);
  
  cam = new PeasyCam(this, 400);

  img = loadImage("output0.png");
  imgRgb = img.get(0, 0, hdim, hdim);
  imgRgb.loadPixels();
  imgX = img.get(hdim, 0, hdim, hdim);
  imgX.loadPixels();
  imgY = img.get(hdim, hdim, hdim, hdim);
  imgY.loadPixels();
  imgZ = img.get(0, hdim, hdim, hdim);
  imgZ.loadPixels();
  
  ps = createShape();
  ps.beginShape(POINTS);
  ps.strokeWeight(strokeWeightVal);
  for (int i=0; i<len; i++) {
    ps.stroke(imgRgb.pixels[i]);
    float x = float(imgX.pixels[i]) / maxIntVal;
    float y = float(imgY.pixels[i]) / maxIntVal;
    float z = float(imgZ.pixels[i]) / maxIntVal;
    ps.vertex(x, y, z);
  }
  ps.endShape();
}

void draw() {
  background(0);
  
  pushMatrix();
  translate(width/8, -height/8, 0);
  scale(scaleVal, scaleVal, scaleVal);
  rotateX(radians(180));
  shape(ps, 0, 0);
  popMatrix(); 

  surface.setTitle("" + frameRate);
}
