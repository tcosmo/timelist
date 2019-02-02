{ pkgs ? import <nixpkgs> {} }:


pkgs.stdenv.mkDerivation rec {
  name = "timelist-${version}";
  version = "0.1";
  src = builtins.fetchGit {
          url = "https://github.com/tcosmo/timelist";
          rev = "f3572e44f0fbf6e3ac6cdd557d3d96dd27fe5de4";
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
