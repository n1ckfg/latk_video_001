class PointsObj {

  ArrayList<PointData> points;
  String[] lines;
  
  PointsObj(String url) {
    lines = loadStrings(url);
    points = new ArrayList<PointData>();
    
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
  }
  
  void draw() {
    beginShape(POINTS);
    for (PointData pd : points) {
      stroke(pd.col);
      vertex(pd.pos.x, pd.pos.y, pd.pos.z);
    }
    endShape();
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
