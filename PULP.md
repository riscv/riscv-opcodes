# Adding a custom ISA extension

If you have a custom ISA extension, create a new file under `extensions/unratified`.
The extension name should be prefixed with an `x` to properly identify custom extensions; refer to the existing extensions.

Finally, list the extension in `pulp-extensions.txt` for it to be picked up as a PULP extension, e.g. by our compiler generation scripts.
