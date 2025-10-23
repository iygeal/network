function editPost(postId) {
  const postContent = document.getElementById(`post-content-${postId}`);
  const originalText = postContent.innerText.trim();

  // Create textarea
  const textarea = document.createElement('textarea');
  textarea.className = 'form-control mb-2';
  textarea.value = originalText;

  // Create Save and Cancel buttons
  const saveButton = document.createElement('button');
  saveButton.className = 'btn btn-sm btn-primary me-2';
  saveButton.innerText = 'Save';

  const cancelButton = document.createElement('button');
  cancelButton.className = 'btn btn-sm btn-secondary';
  cancelButton.innerText = 'Cancel';

  // Replace post content with textarea and buttons (side by side)
  postContent.innerHTML = '';
  const btnContainer = document.createElement('div');
  btnContainer.appendChild(saveButton);
  btnContainer.appendChild(cancelButton);
  postContent.appendChild(textarea);
  postContent.appendChild(btnContainer);

  // Handle Save
  saveButton.onclick = function () {
    const newContent = textarea.value;

    fetch(`/edit/${postId}`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: newContent }),
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.success) {
          // Replace textarea with updated text (preserve line breaks)
          const formatted = newContent.replace(/\n/g, '<br>');
          postContent.innerHTML = formatted;
        } else {
          alert('Error saving post');
        }
      })
      .catch((error) => console.error('Error:', error));
  };

  // Handle Cancel
  cancelButton.onclick = function () {
    // Restore original text (with preserved line breaks)
    const formatted = originalText.replace(/\n/g, '<br>');
    postContent.innerHTML = formatted;
  };
}

// Helper function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
