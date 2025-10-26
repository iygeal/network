(() => {
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
  const csrftoken = getCookie('csrftoken');

  function toggleLike(postId) {
    fetch(`/toggle_like/${postId}`, {
      method: 'PUT',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const likeCount = document.getElementById(`like-count-${postId}`);
          const likeButton = document.getElementById(`like-btn-${postId}`);

          likeCount.innerText = data.likes;
          likeButton.innerText = data.liked ? 'Unlike' : 'Like';
          likeButton.classList.toggle('btn-success', data.liked);
          likeButton.classList.toggle('btn-outline-success', !data.liked);
        } else {
          alert(data.error || 'Error updating like status.');
        }
      })
      .catch((error) => {
        console.error('Like error:', error);
        alert('Network error while toggling like.');
      });
  }

  // Expose globally for templates
  window.toggleLike = toggleLike;
})();
