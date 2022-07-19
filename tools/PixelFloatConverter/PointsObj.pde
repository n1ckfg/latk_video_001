class PointsObj {

  ArrayList<PointData> points;
  String[] lines;
  PShape ps;
  
  PointsObj(String url) {
    ps = createShape();
    lines = loadStrings(url);
    points = new ArrayList<PointData>();
      
    init();
  }
  
  void init() {
    for (int i=0; i<lines.length; i++) {
      if (lines[i].startsWith("v ")) {
        String[] words = lines[i].split(" ");
        PVector pos = new PVector(float(words[1]), float(words[2]), float(words[3]));
        color col = color(255);
        if (words.length == 7) {
          col = color(255 * float(words[4]), 255 * float(words[5]), 255 * float(words[6]));
        }
        PointData pd = new PointData(pos, col);
        points.add(pd);
      }
    }
    
    ps.beginShape(POINTS);
    for (PointData pd : points) {
      ps.stroke(pd.col);
      ps.vertex(pd.pos.x, pd.pos.y, pd.pos.z);
    }
    ps.endShape();
  }
  
  void draw() {
    shape(ps, 0, 0);
  }
  
}

class PointData {
  
  PVector pos;
  color col;
  
  PointData(PVector _pos, color _col) {
    pos = _pos;
    col = _col;
  }
  
}
