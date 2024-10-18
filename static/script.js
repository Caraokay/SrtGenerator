document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    var formData = new FormData();
    var videoFile = document.getElementById('video-file').files[0];
    formData.append('video', videoFile);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').style.display = 'block';
        document.getElementById('srt-link').href = '/download/' + data.srt_path;
        document.getElementById('learning-srt-link').href = '/download/' + data.learning_srt_path;
    })
    .catch(error => console.error('Error:', error));
});
