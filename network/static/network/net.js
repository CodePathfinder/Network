document.addEventListener('DOMContentLoaded', function () {

  document.querySelectorAll('.edit-bttn').forEach(button => {
    button.onclick = function() {
        updatePost(this.dataset.post);
    }
  });

  document.querySelectorAll('.heart-bttn').forEach(button => {
    button.onclick = function() {
      updateLikes(this.dataset.like);
    }
  });
});

function updateLikes(like) {
      
  // GET request to /likes_update route
  let post_id = like.slice(4);
  url = `http://127.0.0.1:8000/likes_update/${post_id}`
  fetch(url)
  .then(response => response.json())
  .then(result => {
    // Print result of API request
    console.log(result);
  
    document.querySelector(`#count_like${post_id}`).innerHTML = result['likes_count'];
  })
  .catch(error => console.log(error));
  return false;
}

// -------------------------------------------------------------

function updatePost(post) {
      
  // Show pre-populated post-update-form and hide post content for selected edit button
  document.querySelector('#form-view').style.display = 'none';
  document.querySelectorAll('.post-update-form').forEach(element => {
    element.style.display = 'none';
  })
  document.querySelectorAll('.post-content').forEach(element => {
    element.style.display = 'block';
  })
  document.querySelector(`#${post}`).style.display = 'block';
  document.querySelector(`#${post}_content`).style.display = 'none';

  // PUT request to /post_update route
  document.querySelector(`#update_${post}`).onsubmit = () => {
    
    let post_id = post.slice(4);
    let url = `http://127.0.0.1:8000/post_update/${post_id}`
    fetch(url, {
    method: 'PUT',
    body: JSON.stringify({
      updated_post: document.querySelector(`#updated_${post}`).value
    })
    })
    .then(response => response.json())
    .then(result => {
      // Print result of PUT request
      console.log(result['content']);
    
      document.querySelector('#form-view').style.display = 'block';
      document.querySelector(`#${post}`).style.display = 'none';
      document.querySelector(`#${post}_content`).style.display = 'block';
      document.querySelector(`#updated_content_${post}`).innerHTML = result['content'];
    })
    .catch(error => console.log(error));
    return false;
  }
}