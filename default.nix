{ pkgs ? import <nixpkgs> {}, pythonPackages ? pkgs.python36Packages }:


pkgs.stdenv.mkDerivation rec {
  name = "timelist-${version}";
  version = "0.1";
  src = ./.;
  propagatedBuildInputs = [
    pythonPackages.markdown

    pythonPackages.flask
    pythonPackages.flask_wtf
    pythonPackages.flask-bootstrap
    pythonPackages.flask_login

    #db
    pythonPackages.flask_sqlalchemy
    pythonPackages.flask_migrate
    pythonPackages.psycopg2
    pythonPackages.werkzeug

    pythonPackages.bibtexparser

  ];

  shellHook = ''export FLASK_APP=timelist.py'';
  installPhase = ''
    mkdir -p $out/lib
    cp -r timelist.py app migrations config.py $out/lib
  '';
}
