# Troubleshooting

## Windows Installer

### More than one python installation

If you have two (or more) different python installations on your computer edit the `openage.bat` in the install directory:
Replace the line `python.exe -m openage` with `call "%INST_DIR%\python\python.exe" -m openage` to start `python.exe` explicitly.

## Asset Conversion

### Error: *No valid game version(s) could not be detected in <folder>*

Check if you have passed the **root folder** of the game to the converter and not a subfolder.

If that doesn't help, you could have a mod installed that messes with the detection algorithm.
In that case, you should reinstall a clean unmodded version of the game and retry the conversion.

### Conversion raises exception when converting *The Conquerors* 1.0c

Make sure you don't have *UserPatch*, compatibility patches or modifications installed that make
changes to the original asset files.

If you have Wololo Kingdoms and various mods installed that change the base assets the converter will not work.
A workaround would be to make a backup of your AGE2 directory and let the converter run on that backup. In that
backup at subfolder `AGE2/resources` delete all files ***except*** folders. Another workaround would be to
backup your AGE2 folder and redownload it to have a clean install. After conversion you can replace
it with the backup.
