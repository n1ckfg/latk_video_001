class PointsObj {

  ArrayList<PointData> points;
  String[] lines;
  PShape ps;
  
  PointsObj(String url) {
    init();
    getLines(url);    
    processPoints();   
  }
  
  PointsObj() {
    init();
  }
  
  void init() {
    ps = createShape();
    points = new ArrayList<PointData>();
  }
  
  void getLines(String url) {
    lines = loadStrings(url);
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
  
  void processPoints() {  
    normalizePoints();
    
    ps = createShape();

    ps.beginShape(POINTS);
    for (PointData pd : points) {
      ps.stroke(pd.col);
      ps.vertex(pd.pos.x, pd.pos.y, pd.pos.z);
    }
    ps.endShape();
  }
  
  void normalizePoints() {
    float minX = 0;
    float maxX = 0;
    float minY = 0;
    float maxY = 0;
    float minZ = 0;
    float maxZ = 0;
    
    for (int i=0; i<points.size(); i++) {
      PointData pd = points.get(i);
      if (pd.pos.x < minX) minX = pd.pos.x;
      if (pd.pos.x > maxX) maxX = pd.pos.x;
      if (pd.pos.y < minY) minY = pd.pos.y;
      if (pd.pos.y > maxY) maxY = pd.pos.y;
      if (pd.pos.z < minZ) minZ = pd.pos.z;
      if (pd.pos.z > maxZ) maxZ = pd.pos.z;
    }
    
    for (int i=0; i<points.size(); i++) {
      PointData pd = points.get(i);
      pd.pos.x = map(pd.pos.x, minX, maxX, 0, 1);
      pd.pos.y = map(pd.pos.y, minY, maxY, 0, 1);
      pd.pos.z = map(pd.pos.z, minZ, maxZ, 0, 1);
    }
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
