{ pkgs ? import <nixpkgs> {}, pythonPackages ? pkgs.python36Packages }:


pkgs.mkShell rec {
  buildInputs = [
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
}