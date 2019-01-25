{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.timelist;
  pkg = pkgs.callPackage /home/tsterin/projects/timelist { };
  pythonEnv = ( pkgs.python36.withPackages (p: pkg.propagatedBuildInputs));
in

{
  options = {
    services.timelist = {
      enable = mkOption {
        type = types.bool;
        default = false;
        description = "Enable the Timelist service.";
      };


      user = mkOption {
        type = types.str;
        default = "timelist";
        description = "User under which Timelist is ran.";
      };

      dataDir = mkOption {
	type = types.str;
	default = "/var/lib/timelist";
	description = "Data directory of the Timelist service";
      };


      group = mkOption {
        type = types.str;
        default = "timelist";
        description = "Group under which Timelist is ran.";
      };

      port = mkOption {
        type = types.int;
        default = 5000;
        description = "Port on which Timelist is ran.";
      };
    };
  };



  config = mkIf cfg.enable {
    
    users.users.timelist = {
	home = cfg.dataDir;	
	group =  "timelist";
	createHome = true;
    };

    users.extraGroups.timelist = {};

    services.postgresql.enable = mkDefault true;
    environment.systemPackages = [ pkg ] ++ pkg.propagatedBuildInputs;
    systemd.services.timelist = {
      
      description = "Timelist is a web service to manage lists of chronological entries :).";

      after = [ "network.target" "postgresql.service" ];
      wantedBy = [ "multi-user.target" ];

      #path = builtins.trace (toString pkg.propagatedBuildInputs) pkg.propagatedBuildInputs;
      path = [ pythonEnv ];
      
      environment = { FLASK_APP = "${pkg.out}/lib/timelist.py"; 
                      PYTHONPATH = "${pythonEnv.out}/lib/python3.6/site-packages";
  			};

      preStart = ''mkdir -p entries'';

      serviceConfig = {
        Type = "simple";
        User = cfg.user;
        Group = cfg.group;
	#TimeoutSec = "300";
        ExecStart=''${pkgs.python36Packages.flask.out}/bin/flask run --port ${toString cfg.port}'';
	WorkingDirectory = ''${cfg.dataDir}'';
      };


    };

  };

}
