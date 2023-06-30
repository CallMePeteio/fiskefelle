
var videoStream = document.getElementById("videoStream");
var loadingCircle = document.getElementById("loadingCircle");
var loadingCircleContainer = document.getElementById("loadingCircleContainer");
var errorContainer = document.getElementById("errorContainer");

function checkStream() {
    fetch('/rtspStreamStatus')  // A new Flask route that returns the status of the stream
        .then(response => response.json())
        .then(data => {
            
            console.log(data.isReadingFrames)
            if (data.isReadingFrames == 404){ // IF THERE WAS AN ERROR CONNECTING TO THE RTSP STREAM
                loadingCircleContainer.style.border = "none";  // Hide the border
                loadingCircleContainer.style.display = "none";  // Hide the border
                loadingCircle.style.display = "none";  // Hide the loading circle

                errorContainer.style.display = "block" // SHOW THE ERROR MESAGE

                
            }
        
            else if (data.isReadingFrames == 1) {  // If the stream has started 
                videoStream.src = "/rtspStream";  // Set the source of the video stream
                errorContainer.style.display = "none" // SHOW THE ERROR MESAGE

                videoStream.style.display = "block";  // Show the video stream
                loadingCircle.style.display = "none";  // Hide the loading circle
                loadingCircleContainer.style.border = "none";  // Hide the border
            } 
            
            else {  // If the stream hasn't started yet
                setTimeout(checkStream, 1000);  // Check again in one second
            }
        });
}
checkStream();  // Start checking the stream status when the page loads
