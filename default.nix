{ pkgs ? import <nixpkgs> {} }:


pkgs.stdenv.mkDerivation rec {
  name = "timelist-${version}";
  version = "0.1";
  src = builtins.fetchGit {
          url = "https://github.com/tcosmo/timelist";
          rev = "df56298d074bed10044e9a56dcf67ff37c9f8071";
	  ref = "to_sql";
        };
  propagatedBuildInputs = [
    pkgs.python36Packages.markdown

    pkgs.python36Packages.flask
    pkgs.python36Packages.flask_wtf
    pkgs.python36Packages.flask-bootstrap
    pkgs.python36Packages.flask_login
    ( pkgs.python36Packages.flask.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.flask_wtf.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.flask-bootstrap.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.flask_login.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.flask_sqlalchemy.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )
    ( pkgs.python36Packages.flask_migrate.overrideAttrs (oldAttrs: { doCheck=false; doInstallCheck=false; }) )

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
