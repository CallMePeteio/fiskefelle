// Pass the value of is_recording from Flask to JavaScript
//var isRecording = {{ is_recording|tojson }};

var isRecording = true;

// Function to fetch data from the API and update the progress bar and text
function updateProgressBar() {
  fetch('/usedVidSpace')
    .then(response => response.json())
    .then(data => {
      // Calculate the percentage of used space
      var percentage = (data.usedSpace / data.maxSpace) * 100;

      // Update the progress bar
      var progressBarFill = document.getElementById('progress-bar-fill');
      progressBarFill.style.width = percentage + '%';
      progressBarFill.setAttribute('aria-valuenow', percentage);

      // Update the text
      var usedSpaceText = document.getElementById('used-space-text');
      usedSpaceText.innerText = `Used Space: ${data.usedSpace}/${data.maxSpace}gb`;
    })
    .catch(error => console.error('Error:', error));
}

// Conditionally call the function based on the value of is_recording
updateProgressBar()
if (isRecording) {
  setInterval(updateProgressBar, 15000);
}