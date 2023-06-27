document.addEventListener('DOMContentLoaded', (event) => {
    function fetchTemperature() {
        fetch('/temperature') 
            .then(response => response.json())
            .then(data => {
                document.getElementById('temperatureDisplay').innerText = 'Temperature: ' + data.temperature + '°C';
            })
            .catch(error => console.error('Error:', error));
    }
  
    // Call fetchTemperature immediately
    fetchTemperature();
  
    // Set interval to call fetchTemperature every 5 seconds
    setInterval(fetchTemperature, 5000);
});