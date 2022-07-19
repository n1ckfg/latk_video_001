class FloatToPixel {
  
  PShape inputShape;
  PGraphics pgRgb, pgX, pgY, pgZ;
  int w, h;
  int len;
  PointsObj po;
  
  FloatToPixel(PointsObj _po) {
    po = _po;  
    
    init();
  }
  
  void init() {
    w = width/2;
    h = height/2;
    
    pgRgb = createGraphics(w, h, P2D);
    pgX = createGraphics(w, h, P2D);
    pgY = createGraphics(w, h, P2D);
    pgZ = createGraphics(w, h, P2D);

    pgRgb.loadPixels();
    pgX.loadPixels();
    pgY.loadPixels();
    pgZ.loadPixels();
    
    if (po.points.size() < w * h){
      len = po.points.size();
    } else {
      len = w * h;
    }
    
    for (int i=0; i<len; i++) {
      PointData pd = po.points.get(i);
      pgRgb.pixels[i] = pd.col;
      pgX.pixels[i] = int(100000 * pd.pos.x);
      pgY.pixels[i] = int(100000 * pd.pos.y);
      pgZ.pixels[i] = int(100000 * pd.pos.z);
    }
    
    pgRgb.updatePixels();
    pgX.updatePixels();
    pgY.updatePixels();
    pgZ.updatePixels();
  }
  
  void draw() {
    image(pgRgb, 0, 0); 
    image(pgX, width/2, 0); 
    image(pgY, width/2, height/2); 
    image(pgZ, 0, height/2); 
  } 
  
}
