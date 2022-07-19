class PixelToFloat {
  
  PointsObj po;
  FloatToPixel f2p;
  
  PixelToFloat(FloatToPixel _f2p) {
    f2p = _f2p;
    po = new PointsObj();   
  }
  
  void draw() {
    po.draw();
  }
  
}
