class PixelToFloat {
  
  FloatToPixel f2p;
  PShape outputShape;
  int len = f2p.w * f2p.h;
  color[] pixelColor = new color[len];
  float[] pixelX = new float[len];
  float[] pixelY = new float[len];
  float[] pixelZ = new float[len];
  
  PixelToFloat(FloatToPixel _f2p) {
    f2p = _f2p;
  }
  
}
