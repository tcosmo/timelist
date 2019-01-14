with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "test";
  buildInputs = [ (import ./default.nix {}) ];
}
