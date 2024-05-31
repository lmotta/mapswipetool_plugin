#!/bin/bash
#
plugin_dir=$( basename $( pwd ) )
# Remove exists file and directory plugi
if [ -f "./$plugin_dir.zip" ]; then
  rm "./$plugin_dir.zip"
fi
if [ -d "./$plugin_dir" ]; then
  rm -r "./$plugin_dir"
fi
# Create Plugin Directory
mkdir "./$plugin_dir"
# Copy files
cp *.py "./$plugin_dir"
for item in metadata.txt LICENSE mapswipetool.png; do cp "./$item" "./$plugin_dir"; done
# Create Translate files
mkdir "./$plugin_dir/i18n"
cp ./i18n/*.ts "./$plugin_dir/i18n"
cd "./$plugin_dir/i18n"
for item in $(ls *.ts); do lrelease -silent $item; rm $item; done
cd ../..
# Create Zip and remove Plugin Directory
zip -q -r "$plugin_dir.zip" "./$plugin_dir"
rm -r "./$plugin_dir"
#
echo "Zip file created: "$plugin_dir".zip"
