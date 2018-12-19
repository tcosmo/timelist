{ pkgs ? import <nixpkgs> {}, pythonPackages ? pkgs.python36Packages }:


pkgs.mkShell rec {
  buildInputs = [
    pythonPackages.flask
    pythonPackages.flask_wtf 

  ];

}
