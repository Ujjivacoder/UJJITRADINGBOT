{ pkgs }: {
  deps = [
    pkgs.glibcLocales
    pkgs.python311Full
    pkgs.gcc
    pkgs.libffi
    pkgs.openssl
    pkgs.zlib
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = "${pkgs.openssl}/lib";
  };
}

