$(function() {
    // Variable to store your files
    var files;

    // Add events
    $('input[type=file]').on('change', prepareUpload);
    $('form').on('submit', uploadFiles);

    // Grab the files and set them to our variable
    function prepareUpload(event) {
        files = event.target.files;
    }

    // Catch the form submit and upload the files
    function uploadFiles(event) {
        event.stopPropagation(); // Stop stuff happening
        event.preventDefault(); // Totally stop stuff happening

        // START A LOADING SPINNER HERE

        // Create a formdata object and add the files
        var data = new FormData();
        $.each(files, function(key, value) {
            data.append(key, value);
        });
        
        $.ajax({
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                //Upload progress
                xhr.upload.addEventListener("progress", function(evt){
                    if (evt.lengthComputable) {
                        var percentComplete = (evt.loaded / evt.total) * 100;
                      //Do something with upload progress
                        var progressBar = document.getElementById("bar");
                        progressBar.style.display = 'block';
                        var text = progressBar.childNodes[1].childNodes[1];
                        text.innerHTML = percentComplete + '%';
                        progressBar.style.width = text.innerHTML;
                    }
                }, false);
                return xhr;
            },
            url: '/api/v1.0/file',
            headers: {"X-HTTP-Method-Override": "PUT"}, // X-HTTP-Method-Override set to PUT.
            type: 'PUT',
            method: 'PUT',
            data: data,
            cache: false,
            dataType: 'json',
            processData: false, // Don't process the files
            contentType: false, // Set content type to false as jQuery will tell the server its a query string request
            success: function(data, textStatus, jqXHR) {
                if(typeof data.error === 'undefined') {
                    // Success so call function to process the form
                    var a = document.createElement('a');
                    var filelist = document.getElementById("filelist");
                    var entry = document.createElement('li');
                    var linkText = document.createTextNode(data.url);
                    a.appendChild(linkText);
                    a.title = data.url 
                    a.href = data.url;
                    entry.appendChild(a)
                    filelist.appendChild(entry)
                    var progressBar = document.getElementById("bar");
                    progressBar.style.display = 'none';
    
                }
                else {
                    // Handle errors here
                    console.log('ERRORS: ' + data.error);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // Handle errors here
                console.log('ERRORS: ' + textStatus);
                alert("Please keep uploads limited to 16MB for now")
                // STOP LOADING SPINNER
            }
        });
    }
});
