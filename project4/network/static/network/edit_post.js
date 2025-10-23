
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

function editPost(postId) {
  const postContent = document.getElementById(`post-content-${postId}`);
  if (!postContent) return;

  const originalText = postContent.innerText.trim();

  // Create textarea
  const textarea = document.createElement("textarea");
  textarea.className = "form-control mb-2";
  textarea.rows = 4;
  textarea.value = originalText;

  // Save + Cancel (inline, horizontal)
  const saveButton = document.createElement("button");
  saveButton.className = "btn btn-sm btn-primary me-2";
  saveButton.type = "button";
  saveButton.innerText = "Save";

  const cancelButton = document.createElement("button");
  cancelButton.className = "btn btn-sm btn-secondary";
  cancelButton.type = "button";
  cancelButton.innerText = "Cancel";

  // Buttons container (keeps them horizontal)
  const btnContainer = document.createElement("div");
  btnContainer.className = "mt-2";
  btnContainer.appendChild(saveButton);
  btnContainer.appendChild(cancelButton);

  // Replace content with textarea + buttons
  postContent.innerHTML = "";
  postContent.appendChild(textarea);
  postContent.appendChild(btnContainer);

  // Cancel restores original (preserving line breaks)
  cancelButton.onclick = function () {
    postContent.innerHTML = nl2br(escapeHtml(originalText));
  };

  // Save -> PUT to backend
  saveButton.onclick = function () {
    const newContent = textarea.value;

    fetch(`/edit_post/${postId}`, {
      method: "PUT",
      headers: {
        "X-CSRFToken": csrftoken,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ content: newContent })
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
      if (status >= 200 && status < 300 && body.success) {
        // Update DOM: show formatted content with line breaks
        postContent.innerHTML = nl2br(escapeHtml(body.new_content));
      } else {
        // Show helpful error
        const msg = body.error || "Unable to save post";
        alert(msg);
      }
    })
    .catch(error => {
      console.error("Edit error:", error);
      alert("Network error while saving post");
    });
  };
}

// Utility: convert newline chars to <br>
function nl2br(str) {
  return str.replace(/\r\n|\r|\n/g, "<br>");
}

// Utility: escape HTML to avoid XSS, then used with nl2br
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Expose function globally so onclick handlers in template can call it
window.editPost = editPost;
