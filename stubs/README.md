# Gimp Stubs Generation

Gimp Stubs are generated using the python stub generator - [pygobject-stubs](https://github.com/pygobject/pygobject-stubs)

Issues with [PyCharm generator3](https://github.com/JetBrains/intellij-community/tree/master/python/helpers/generator3):

- The generates files are too big for IDEs (Gtk > 20Mb, GimpUI > 7.5 Mb) which doesn't go as well with Pycharm itself
- The generated output also doesn't have the correct type-definitions Eg: `Gimp.Layer.new(...)` - first argument is self, but actually it's a static method.

These issues aren't there in `pygobject-stubs` generator.

## Commands

- Create the virualenv (using gimp's python executable)

   ```sh
   stubs/setup.sh
   ```

- Generate stubs - inside the venv (directly gimp's python executable will be used to generate stubs)

   ```sh
   stubs/generate.sh
   ```
