class FloatToPixel {
  
  PShape inputShape;
  PGraphics pgRgb, pgX, pgY, pgZ;
  int w, h;
  int len;
  color[] pixelColor;
  float[] pixelX, pixelY, pixelZ;
  
  FloatToPixel() {
    w = width/2;
    h = height/2;
    pgRgb = createGraphics(w, h);
    pgX = createGraphics(w, h);
    pgY = createGraphics(w, h);
    pgZ = createGraphics(w, h);
    
    len = w * h;
    pixelColor = new color[len];
    pixelX = new float[len];
    pixelY = new float[len];
    pixelZ = new float[len];
    
    init();
  }
  
  void init() {
    pgRgb.beginDraw();
    pgRgb.background(127);
    pgRgb.endDraw();

    pgX.beginDraw();
    pgX.background(127, 0, 0);
    pgX.endDraw();
    
    pgY.beginDraw();
    pgY.background(0, 127, 0);
    pgY.endDraw();
    
    pgZ.beginDraw();
    pgZ.background(0, 0, 127);
    pgZ.endDraw();
  }
  
  void draw() {
    image(pgRgb, 0, 0); 
    image(pgX, width/2, 0); 
    image(pgY, width/2, height/2); 
    image(pgZ, 0, height/2); 
  } 
  
}
