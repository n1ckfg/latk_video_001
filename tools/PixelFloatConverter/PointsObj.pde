class PointsObj {

  ArrayList<PointsObjChild> obj;
 
  PointsObj(PShape _shape) {
    obj = new ArrayList<PointsObjChild>();
    
    for (int i=0; i<_shape.getChildCount(); i++) {
      obj.add(new PointsObjChild(_shape.getChild(i)));
    }
  }
  
  void draw() {
    for (int i=0; i<obj.size(); i++) {
      obj.get(i).draw();
    }
  }
  
}

class PointsObjChild {

  ArrayList<PointData> points;

  PointsObjChild(PShape _shape) {
    points = new ArrayList<PointData>();
    
    for (int i=0; i<_shape.getVertexCount(); i++) {
      color col = color(0);
      try {
        col = _shape.getStroke(0);
      } catch (Exception e) {
        try {
          col = _shape.getFill(0);
        } catch (Exception ee) { }
      }
      PointData p = new PointData(_shape.getVertex(i), col);
      points.add(p);
    }
  }
  
  void draw() { 
    beginShape(POINTS);
    for (int i=0; i<points.size(); i++) {
      PVector p = points.get(i).pos;
      stroke(255);
      vertex(p.x, p.y, p.z);
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
