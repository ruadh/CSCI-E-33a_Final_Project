// Initial page load
document.addEventListener('DOMContentLoaded', function () {

  // Confirm that we've loaded the page
  // alert('page load!');

    // Add listeners to the Add to Cart buttons
    document.querySelectorAll('.add-button').forEach(button => {
      button.addEventListener('click', () => addToCart(button.dataset.offering));
    });
});

/**
 * Add a class to the cart
 */

function addToCart(id) {
  // alert(id);

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const addButton = document.querySelector(`.add-button[data-offering="${id}"]`);
  addButton.disabled = true;
  // alert(id);

  // TO DO:  CSRF
  // Gather the CSRF token from the Django template
  // CITATION:  Copied directly from Vlad's section slides
  // const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;


  // Add the offering to the cart via the API
  fetch(`/add-to-cart/${id}`, {
    method: 'POST'
  })
    .then(response => response.json())
    .then(item => {

      if (item.error == undefined) {
        // alert(item.stored_title);
        alert('success?');
      } else {
        alert(item.error);
      }

      // Reenable the like/dislike button
      addButton.disabled = false;
    });

}
