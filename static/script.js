document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    const resultDisplay = document.getElementById('result');

    uploadForm.onsubmit = async function(event) {
        event.preventDefault();
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });
            const data = await response.json();
            resultDisplay.textContent = `Similarity Score: ${data.similarity_score || "Error"}`;
        } catch (error) {
            console.error('Error uploading file:', error);
            resultDisplay.textContent = 'Error calculating similarity score.';
        }
    };
});
