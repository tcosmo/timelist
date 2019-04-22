{ pkgs ? 

import (builtins.fetchGit {
  # Descriptive name to make the store path easier to identify
  name = "nixos-unstable-2018-Apr-21";
  url = https://github.com/nixos/nixpkgs/;
  # Commit hash for nixos-unstable as of 2018-09-12
  # `git ls-remote https://github.com/nixos/nixpkgs-channels nixos-unstable`
  rev = "ea9161e0955fd9fcc330471464f24ebc4aedaae1";
}) {}

 }:


pkgs.stdenv.mkDerivation rec {
  name = "timelist-${version}";
  version = "0.1";
  src = builtins.fetchGit {
          url = "https://github.com/tcosmo/timelist";
          rev = "ca653e5224df3e405602e162721de08287e6ba20";
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
