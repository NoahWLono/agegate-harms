# Momiji bundle packaging

`install-on-momiji.fish` and `install-on-momiji.sh` are copied to the root of the Momiji release bundle. The bundle builder places the clean project tree in a sibling `project/` directory. The installer is not intended to be run directly from this source directory because `packaging/project/` does not exist.
