void keyPressed() {
  switch(key) {
    case('1'):
      gs = GameState.OBJ;
      break;
    case('2'):
      gs = GameState.F2P;
      break;
    case('3'):
      gs = GameState.P2F;
      break;
    case('s'):
      saveFrame();
      break;
  }
}
