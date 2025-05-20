document.getElementById('submit-btn').addEventListener('click', function (event) {
    event.preventDefault(); // Prevent form submission if inside a form

    const submitButton = event.currentTarget;
    const persona = document.getElementById('persona').value;
    const question = document.getElementById('question').value;
    const aiInfo = document.querySelector('.ai-info');
    const outputArea = document.getElementById('answer');
    const avatarImg = document.querySelector('.ai-avatar');

    // Button pop animation
    submitButton.classList.add('pop');
    setTimeout(() => submitButton.classList.remove('pop'), 300);

    // Remove all persona classes
    aiInfo.classList.remove('persona-friendly', 'persona-professional', 'persona-humorous');

    // Add the selected persona class
    if (persona === 'friendly') {
        aiInfo.classList.add('persona-friendly');
        avatarImg.src = '/static/img/avatar-friendly.png';
    } else if (persona === 'professional') {
        aiInfo.classList.add('persona-professional');
        avatarImg.src = '/static/img/avatar-professional.png';
    } else if (persona === 'humorous') {
        aiInfo.classList.add('persona-humorous');
        avatarImg.src = '/static/img/avatar-humorous.png';
    } else {
        avatarImg.src = '/static/img/default-avatar.png';
    }

    // Fetch AI response from FastAPI backend
console.log(`Fetching response for question: ${question}, persona: ${persona}`);
fetch(`/ask?question=${encodeURIComponent(question)}&persona=${encodeURIComponent(persona)}`)
    .then(response => {
        console.log(`Response status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        const answer = data.answer;
        if (answer) {
            typeOutText(answer, outputArea);
        } else {
            outputArea.textContent = 'No response received from the AI.';
        }
    })
    .catch(error => {
        console.error('Error fetching response:', error);
        outputArea.textContent = 'Sorry, something went wrong. Please try again.';
    }); 
});


// Typing effect function (make sure this exists somewhere in your JS)
function typeOutText(text, element) {
    element.innerHTML = ''; // Clear previous content
    element.style.opacity = 0;
    let index = 0;

    const interval = setInterval(() => {
        if (index < text.length) {
            element.innerHTML += text[index];
            index++;
        } else {
            clearInterval(interval);
            element.style.transition = 'opacity 1s';
            element.style.opacity = 1; // Fade in after typing
        }
    }, 50); // Adjust speed here
}

