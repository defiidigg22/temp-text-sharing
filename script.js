// Get references to the HTML elements
const saveButton = document.getElementById('saveButton');
const contentText = document.getElementById('contentText');
const expiresIn = document.getElementById('expiresIn');
const resultDiv = document.getElementById('result');

// Listen for a click on the save button
saveButton.addEventListener('click', async () => {
    // Get the data from the input fields
    const data = {
        content: contentText.value,
        expiresIn: expiresIn.value
    };

    try {
        // Send the data to your FastAPI backend using the fetch API
        const response = await fetch('http://127.0.0.1:8000/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            // If the server response is not OK, throw an error
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Something went wrong');
        }

        const result = await response.json();
        
        // Display the successful result
        const snippetUrl = `http://127.0.0.1:8000${result.url}`;
        resultDiv.innerHTML = `Success! Your link is: <a href="${snippetUrl}" target="_blank">${snippetUrl}</a>`;

    } catch (error) {
        // Display any errors
        resultDiv.innerHTML = `Error: ${error.message}`;
        resultDiv.style.color = 'red';
    }
});