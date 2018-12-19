{ pkgs ? import <nixpkgs> {}, pythonPackages ? pkgs.python36Packages }:


pkgs.mkShell rec {
  buildInputs = [
    pythonPackages.markdown

    pythonPackages.flask
    pythonPackages.flask_wtf 
    pythonPackages.flask-bootstrap
    pythonPackages.bibtexparser

  ];

  shellHook = ''export FLASK_APP=timelist.py''
}