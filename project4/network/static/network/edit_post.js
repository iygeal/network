function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function editPost(postId) {
    const contentElement = document.getElementById(`post-content-${postId}`);
    const originalContent = contentElement.innerText;

    contentElement.outerHTML = `
      <textarea id="edit-area-${postId}" class="form-control mb-2">${originalContent}</textarea>
      <button class="btn btn-sm btn-success" onclick="savePost(${postId})">Save</button>
      <button class="btn btn-sm btn-secondary" onclick="cancelEdit(${postId}, '${originalContent.replace(/'/g, "\\'")}')">Cancel</button>
    `;
}

function cancelEdit(postId, originalContent) {
    const textarea = document.getElementById(`edit-area-${postId}`);
    textarea.outerHTML = `<p class="card-text" id="post-content-${postId}">${originalContent}</p>`;
}

function savePost(postId) {
    const newContent = document.getElementById(`edit-area-${postId}`).value.trim();

    fetch(`/edit_post/${postId}`, {
        method: "PUT",
        headers: { "X-CSRFToken": csrftoken },
        body: JSON.stringify({ content: newContent })
    })
    .then(response => response.json())
    .then(result => {
        if (result.new_content) {
            document.getElementById(`edit-area-${postId}`).outerHTML =
              `<p class="card-text" id="post-content-${postId}">${result.new_content}</p>`;
        } else if (result.error) {
            alert(result.error);
        }
    })
    .catch(error => console.error("Error:", error));
}
