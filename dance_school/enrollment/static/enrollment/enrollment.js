// Initial page load
document.addEventListener('DOMContentLoaded', function () {

  // Confirm that we've loaded the page
  // alert('page load!');

  // Add listeners to the Add to Cart buttons
  // TO DO:  Replace them with text if registration isn't open yet
  document.querySelectorAll('.add-button').forEach(button => {
    button.addEventListener('click', () => addToCart(button.dataset.offering));
  });

  // Add listeners to the Remove from Cart buttons
  document.querySelectorAll('.remove-button').forEach(button => {
    button.addEventListener('click', () => removeFromCart(button.dataset.item));
  });

  // Add listeners to the Checkout button  (there should only be 1, but forEach handles missing buttons gracefully)
  document.querySelectorAll('#checkout-button').forEach(button => {
    button.addEventListener('click', () => checkout(button.dataset.order));
  });

  // Add listeners to the Edit Profile button (there should only be 1, but forEach handles missing buttons gracefully)
  document.querySelectorAll('#edit-profile-button').forEach(button => {
    button.addEventListener('click', () => profileForm(button.dataset.profile));
  });
});

/**
 * Add an offering to the cart
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
  fetch(`/cart/${id}`, {
    method: 'POST'
  })
    .then(response => response.json())
    .then(lineItem => {

      if (lineItem.error == undefined) {
        // TO DO:  Update cart view  (for now just refreshing - don't forget to update totals)
        location.reload();
      } else {
        // TO DO:  Add error handling via messages?
        alert(lineItem.error);
      }

      // Reenable the add button
      addButton.disabled = false;
    });

}

/**
 * Remove a line item from the cart
 */

function removeFromCart(id) {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const removeButton = document.querySelector(`.remove-button[data-item="${id}"]`);
  removeButton.disabled = true;

  // Add the offering to the cart via the API
  fetch(`/cart/${id}`, {
    method: 'DELETE'
  })
    .then(response => response.json())
    .then(lineItem => {

      if (lineItem.error == undefined) {
        // TO DO:  Update cart view  (for now just refreshing - don't forget to update totals)
        location.reload();
      } else {
        // TO DO:  Add error handling via messages?
        alert(lineItem.error);
      }

      // Reenable the add button
      removeButton.disabled = false;
    });

}



/**
 * Remove a line item from the cart
 */

function checkout(id) {
  alert(id);

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const checkoutButton = document.querySelector('#checkout-button');
  checkoutButton.disabled = true;

  // Submit the cart via the API
  fetch(`/checkout/${id}`, {
    method: 'POST'
  })
    .then(response => response.json())
    .then(order => {

      // TO DO:  What happens after we get a response back?
      if (order.error == undefined) {
        alert('success...?');
      } else {
        alert(order.error);
      }

      // Reenable the add button
      checkoutButton.disabled = false;
    });
}

/**
* Replace editable profile values with form fields
*/

// TO DO:  write about dependency that element must be value inside editable

function profileForm(id) {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const editButton = document.querySelector('#edit-profile-button');
  editButton.disabled = true;

  // Disable the cart submit button, if present  (Again: using querySelectorAll to gracefully handle missing elements)
  document.querySelectorAll('#submit-cart-button').forEach(button => {
    button.setAttribute('disabled','disabled')
  });


  // TEMP FOR TESTING:
  // alert(`profileForm ${id}`);

  // Replace the contents of each editable value with an input, populated with the current value
  const fieldsList = document.querySelectorAll('.editable .value');
  fieldsList.forEach(field => {
    const fieldValue = field.innerHTML;
    field.innerHTML = '';
    const child = document.createElement('input');
    child.id = field.id;
    child.value = fieldValue;
    field.appendChild(child);
  })

  // Replace the edit button with a Save button
  swapProfileButtons('edit','save');
}

/**
* Save the edit profile form
*/

function saveProfile(id) {
  alert(`saveProfile ${id}`);

  //  TO DO:  Get the token
  // Gather the CSRF token from the Django template
  // CITATION:  Copied directly from Vlad's section slides
  // const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  // alert(token);


  
  //  TO DO:  prep content

  // Update the profile's contents via the API
  // fetch(`/posts/${id}`, {
  //   method: 'PUT',
  //   body: JSON.stringify({
  //     content: content
  //   }),
  //   headers: {
  //     'X-CSRFToken': token
  //   }
  // })
  // .then(response => response.json())
  // .then(post => {


  //   // If successful, update the page
  //   if (post.error == undefined) {

  //     // Replace the pseudo-form with the updated post contents
  //     const contents = document.querySelector(`.post-row[data-post="${id}"] .post-content`);
  //     contents.innerHTML = post.content;

  //     // Reenable the edit button
  //     const editButton = document.querySelector(`.post-row[data-post="${id}"] .edit-button`);
  //     editButton.disabled = false;

  //   } else {
  //     // Display an alert above the post
  //     // DESIGN NOTE:  I'm repeating a queryselector, but I think that's better than storing the object,
  //     //               since this block will not usually be executed - only if there's an error.
  //     displayAlert(document.querySelector(`.post-row[data-post="${id}"] .alert`), post.error, 'danger');

  //   }

  //   // Reenable the like/dislike button to try again
  //   saveButton.disabled = false;

  // });

      // Replace the save button with an edit button
      swapProfileButtons('save','edit');

      // Reenable the submit cart button, if present  (Again: using querySelectorAll to gracefully handle missing elements)
      document.querySelectorAll('#submit-cart-button').forEach(button => {
        button.removeAttribute('disabled')
      });

    }


/**
* Helper function:  Swap the Edit Profile and Save Profile buttons
 * @param {string} from - the button type to be removed, either 'edit' or 'save' in lowercase
 * @param {string} to - the button type to be added, either 'edit' or 'save' in lowercase
*/

function swapProfileButtons(from, to) {

  // TO DO:  detect the direction of the swap based on which buttons are on the page
  // OR:     maybe just accept from and calculate to
  
  // Validate the parameters
  if ( (from != 'edit' && from != 'save') || (to != 'edit' && to != 'save')){
    return;
  }

  const oldButton = document.querySelector(`#${from}-profile-button`);
  const newButton = document.createElement('button');
  newButton.id = `${to}-profile-button`;
  newButton.dataset.profile = oldButton.dataset.profile;
  // Button text will be capitalized by CSS, but let's apply that again here in case that changes or is overriden
  // CITATION:  https://flaviocopes.com/how-to-uppercase-first-letter-javascript/
  newButton.innerHTML = `${to.charAt(0).toUpperCase()}${to.slice(1)}`;
  newButton.addEventListener('click', () => saveProfile(oldButton.dataset.profile));
  oldButton.after(newButton);
  oldButton.remove();

}






