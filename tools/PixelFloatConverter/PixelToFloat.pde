class PixelToFloat {
  
  PointsObj po;
  
  PixelToFloat(FloatToPixel _f2p) {
    po = new PointsObj();   
    
   for (int i=0; i<_f2p.len; i++) {
      color col = _f2p.pgRgb.pixels[i];
      float x = float(_f2p.pgX.pixels[i]) / _f2p.maxIntVal;
      float y = float(_f2p.pgY.pixels[i]) / _f2p.maxIntVal;
      float z = float(_f2p.pgZ.pixels[i]) / _f2p.maxIntVal;
      PointData pd = new PointData(new PVector(x, y, z), col);
      po.points.add(pd);
    }
    
    po.processPoints();
  }
  
  void draw() {
    po.draw();
  }
  
}
