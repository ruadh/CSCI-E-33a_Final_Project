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

function profileForm(id) {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const editButton = document.querySelector('#edit-profile-button');
  editButton.disabled = true;

  alert(`profileForm ${id}`);

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

  // Replace the edit button with a save button
  editButton.innerHTML = 'Save'
  // TO DO:  Figure out how to remove existing listener
  editButton.removeEventListener('click', profileForm)
  editButton.addEventListener('click', () => saveProfile(id));
  editButton.disabled = false;
}

/**
* Save the edit profile form
*/

function saveProfile(id) {
  alert(`saveProfile ${id}`);
}