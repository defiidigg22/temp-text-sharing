// script.js

const saveButton = document.getElementById('saveButton');
const contentText = document.getElementById('contentText');
const expiresIn = document.getElementById('expiresIn');
const resultDiv = document.getElementById('result');

saveButton.addEventListener('click', async () => {
    const data = {
        content: contentText.value,
        expiresIn: expiresIn.value
    };

    try {
        const response = await fetch('/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Something went wrong');
        }

        const result = await response.json();
        
        // This line is updated to build the full, correct URL
        const snippetUrl = `${window.location.origin}${result.url}`;
        
        resultDiv.innerHTML = `Success! Your link is: <a href="${snippetUrl}" target="_blank">${snippetUrl}</a>`;

    } catch (error) {
        resultDiv.innerHTML = `Error: ${error.message}`;
        resultDiv.style.color = 'red';
    }
});