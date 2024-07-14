###################################
# Installation using shell script #
###################################

chmod +x TravelPlaner
sudo mv TravelPlaner /usr/bin
sudo mkdir /etc/TravelPlaner
if [ -f setting.ini ]; then
   sudo mv setting.ini /etc/TravelPlaner
fi
