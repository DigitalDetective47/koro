koro (stylized in all lowercase) is a Python package that can read and modify stages from *Marble Saga: Kororinpa*.

# *Marble Saga: Kororinpa*

*Marble Saga: Kororinpa* is a video game released for the Nintendo Wii in March of 2009 in North America; the game was released in PAL regions under the title *Marbles! Balance Challenge* in May of the same year. Like its predecessor *Kororinpa*/*Kororinpa: Marble Mania*, it is a ball&hyphen;rolling game which is very similar to the *Super Monkey Ball* series in which the player character is controlled by tilting the game world. This game makes use of the Wii Remote's motion control capabilities by using the orientation of the controller to manipulate the world.

# Problems

*Marble Saga: Kororinpa* included a stage editor in which parts could be created by combining junk parts collected within the main game. The game provides the player with 20 slots in which to save stages that they have created. During the time period following the game's release, players could share their created stages using the WiiConnect24 service. After WiiConnect24 shut down on the 28<sup>th</sup> of June 2013, sharing stages with other players became impossible through official means. Sharing save files is not possible through the Wii system menu as the game had online leaderboards for ten stages specifically designed for online competition. As a result, saves of this game are marked as protected and cannot be copied from the save manager present in the Wii system menu.

# This package

This package allows you to extract the saved stages from your save file and store them in their own files, and to import stages downloaded online into your existing save file. (This package does not provide tools to get saves to or from the Wii console, there is plenty of homebrew software already in existence for this purpose.) This package also contains reverse&hyphen;engineered replicas of the game's compression format used internally, allowing for stage substitution in mods.

# Usage

To install this package, simply run
```
pip install koro
```
in a command prompt. For detailed documentation of the contents of the package, please view the wiki. For basic users, simple command&hyphen;line tools are available in the `scripts` folder of this repository. **Use of these tools requires installing the package from PyPI.**

## Playing downloaded stages

`unpacker.py` is a script designed to inject stages downloaded online into your save file. Simply run the script with the stages, the data directory of your save file, and if injecting a single stage, the slot to inject it into. The stages should then appear in the **Friend** tab. To find the location of your save in Dophin, right&hyphen;click the game and select **Open Wii Save Folder**.

## Uploading your stages

`packer.py` is a script that allows you to easily extract and upload stages that you've created. Run the script with your save directory, destination (ZIP archive), and optionally which stages to export. This script only exports stages stored in the **Original** tab of the editor. To specify which stages to export, simply enter the stage numbers in the order that they should appear when downloaded. If a custom ordering is not specified, the default is to extract all 20 stages in the order that they appear in&hyphen;game. To share single levels, extract files from the resulting archive.
