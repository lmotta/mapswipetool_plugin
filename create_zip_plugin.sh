#!/bin/bash
plugin_dir=$( basename $( pwd ) )
if [ -f "./$plugin_dir.zip" ]; then
  rm "./$plugin_dir.zip"
fi
mkdir "./$plugin_dir"
cp *.py "./$plugin_dir"
for item in metadata.txt README.md LICENSE mapswipetool.png; do cp "./$item" "./$plugin_dir"; done
mkdir "./$plugin_dir/i18n"
cp ./i18n/*.qm "./$plugin_dir/i18n"
zip -r $plugin_dir $plugin_dir
rm -r $plugin_dir
#
kdialog --msgbox "Zip file created: "$plugin_dir".zip"


