{
  description = "Tailscale Tailnet Name Searcher";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        py3libs = with pkgs.python3.pkgs; [
          requests
        ];
      in
      {
        packages = {
          default = pkgs.writers.writePython3Bin "tailnet-name-searcher" {
            libraries = py3libs;
          } (builtins.readFile ./main.py);
        };

        devShells = {
          default = pkgs.mkShell {
            buildInputs = [
              pkgs.python3.withPackages
              (_: py3libs)
            ];
          };
        };
      }
    );
}
