sudo service mosquitto start

# Check if the service is running
echo "Checking Mosquitto service status..."
sudo service mosquitto status

# Check if port 1883 is open
echo "Checking if port 1883 is listening..."
netstat -tuln | grep 1883

# If not running, start manually with our config
if [ $? -ne 0 ]; then
    echo "Starting Mosquitto manually..."
    sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
fi
