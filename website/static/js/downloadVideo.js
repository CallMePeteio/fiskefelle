document.querySelectorAll('.downloadLink').forEach(function(downloadLink) {  // SELECT ALL ELEMENTS WITH THE CLASS 'DOWNLOADLINK'
    downloadLink.addEventListener('click', function(event) {  // ADD AN EVENT LISTENER FOR A CLICK EVENT ON EACH 'DOWNLOADLINK'
      event.preventDefault();  // PREVENT THE DEFAULT ACTION OF THE CLICK EVENT
      var downloadUrl = this.href;  // STORE THE HREF VALUE OF THE CLICKED LINK IN 'DOWNLOADURL'

      var download = document.createElement('a');  // CREATE A NEW ANCHOR ELEMENT
      download.href = downloadUrl;  // SET THE HREF OF THE NEW ANCHOR TO THE 'DOWNLOADURL'
      download.download = '';  // SET THE DOWNLOAD ATTRIBUTE OF THE ANCHOR TO AN EMPTY STRING
      download.click();  // TRIGGER A CLICK EVENT ON THE NEW ANCHOR, STARTING THE DOWNLOAD

      setTimeout(function(){  // SET A TIMEOUT TO DELAY THE REDIRECTION
          window.location = "/video";  // REDIRECT TO THE '/VIDEO' ROUTE AFTER THE DELAY
      }, 1000);  // DELAY IS SET TO 1 SECOND (1000 MILLISECONDS), ADJUST IF NECESSARY
    });
  });