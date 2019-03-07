{ pkgs ? import <nixpkgs> {} }:


pkgs.stdenv.mkDerivation rec {
  name = "timelist-${version}";
  version = "0.1";
  src = builtins.fetchGit {
          url = "https://github.com/tcosmo/timelist";
          rev = "f52999712378628e206d33b13a8f4e4330ed7016";
	  ref = "to_sql";
        };
  propagatedBuildInputs = [
    pkgs.python36Packages.markdown


    ( pkgs.python36Packages.flask.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.flask_wtf.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.flask-bootstrap.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.flask_login.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    #( pkgs.python36Packages.flask_sqlalchemy.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.flask_migrate.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.passlib.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )

    #db
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
