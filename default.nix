{ pkgs ? import <nixpkgs> {} }:


pkgs.stdenv.mkDerivation rec {
  name = "timelist-${version}";
  version = "0.1";
  src = builtins.fetchGit {
          url = "https://github.com/tcosmo/timelist";
          rev = "2643a52b6a3f14d9fa6e2dd2fdd5d02e7265905e";
	  ref = "to_sql";
        };
  propagatedBuildInputs = [
    pkgs.python36Packages.markdown

    pkgs.python36Packages.flask
    pkgs.python36Packages.flask_wtf
    pkgs.python36Packages.flask-bootstrap
    pkgs.python36Packages.flask_login
    ( pkgs.python36Packages.passlib.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )

    #db
    pkgs.python36Packages.flask_sqlalchemy
    pkgs.python36Packages.flask_migrate
    pkgs.python36Packages.psycopg2
    pkgs.python36Packages.werkzeug

    pkgs.python36Packages.bibtexparser

  ];


  shellHook = ''export FLASK_APP=timelist.py'';
  installPhase = ''
    mkdir -p $out/lib
    cp -r timelist.py app migrations config.py $out/lib
  '';
}
