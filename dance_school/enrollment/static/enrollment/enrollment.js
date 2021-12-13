// Initial page load
document.addEventListener('DOMContentLoaded', function () {

  // Add listeners to the Add to Cart buttons
  document.querySelectorAll('.add-button').forEach(button => {
    button.addEventListener('click', () => addToCart(button.dataset.offering));
  });

  // Add listeners to the Remove from Cart buttons
  document.querySelectorAll('.remove-button').forEach(button => {
    button.addEventListener('click', () => removeFromCart(button.dataset.item));
  });

  // Add listeners to the Edit Profile button (there should only be one, but forEach handles missing buttons gracefully)
  document.querySelectorAll('#edit-profile-button').forEach(button => {
    button.addEventListener('click', () => profileForm(button.dataset.profile));
  });
});


/**
 * Add an offering to the cart
 * @param {integer} id - the ID of the offering to be added
 */

function addToCart(id) {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const addButton = document.querySelector(`.add-button[data-offering="${id}"]`);
  addButton.disabled = true;

  // Gather the CSRF token from the Django template
  const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  // Add the offering to the cart via the API
  fetch(`/cart/${id}`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': token
    }
  })
    .then(response => response.json())
    .then(lineItem => {

      if (lineItem.error == undefined) {
        location.reload();
      } else {
        alert(lineItem.error);
      }

      // Reenable the add button
      addButton.disabled = false;
    });

}


/**
 * Remove a line item from the cart
 * @param {integer} id - the ID of the line item to be removed
 */

function removeFromCart(id) {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const removeButton = document.querySelector(`.remove-button[data-item="${id}"]`);
  removeButton.disabled = true;

  // Gather the CSRF token from the Django template
  const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  // Add the offering to the cart via the API
  fetch(`/cart/${id}`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': token
    }
  })
    .then(response => response.json())
    .then(lineItem => {

      if (lineItem.error == undefined) {
        location.reload();
      } else {
        alert(lineItem.error);
      }

      // Reenable the add button
      removeButton.disabled = false;
    });

}


/**
 * Replace editable profile values with form fields
 * 
 * Dependency:  This will only affect DOM elements with class "value" inside a parent element of class "editable"
 */

function profileForm() {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const editButton = document.querySelector('#edit-profile-button');
  editButton.disabled = true;

  // Disable the cart submit button, if present  (Again: using querySelectorAll to gracefully handle missing elements)
  document.querySelectorAll('#submit-cart-button').forEach(button => {
    button.setAttribute('disabled', 'disabled');
  });

  // Replace the contents of each editable value with an input, populated with the current value
  document.querySelectorAll('.editable .value').forEach(field => {
    const fieldValue = field.innerHTML;
    field.innerHTML = '';
    newElement('input', null, 'value', field.id, fieldValue, field);
  });

  // Replace the edit button with a Save button
  swapProfileButtons('edit');

}


/**
 * Save the edit profile form
 * @param {integer} id - the ID of the profile being edited
 */

function saveProfile(id) {

  // Gather the CSRF token from the Django template
  const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  // Disable the cancel and save buttons, so they can't click repeatedly while waiting
  const saveButton = document.querySelector('#save-profile-button');
  saveButton.disabled = true;
  const cancelButton = document.querySelector('#cancel-button');
  cancelButton.disabled = true;


  // Bundle the pseudo-form values to pass
  const body = {};
  const fieldsList = document.querySelectorAll('.editable .value');
  let errorCt = 0;
  fieldsList.forEach(field => {
    // Make sure the value is not empty, then add the key/value pair  (consider further validation in future)
    if (field.value.trim() == '') {
      errorCt++;
    } else {
      body[field.id] = field.value.trim();
    }
  });

  if (errorCt == 0) {

    // Update the profile's contents via the API
    fetch(`/users/${id}`, {
      method: 'POST',
      body: JSON.stringify(body),
      headers: {
        'X-CSRFToken': token
      }
    })
      .then(response => response.json())
      .then(profile => {

        // If successful, update the page
        if (profile.error == undefined) {

          // Replace the pseudo-form with the updated profile contents
          // CITATION: https://stackoverflow.com/a/34913701/15100723
          for (const [fieldName, fieldValue] of Object.entries(profile)) {
            // Replace the contents of each input with its updated value, as returned from the API
            const input = document.querySelector(`#${fieldName}`);
            newElement('span', fieldValue, 'value', fieldName, null, input);
          }

          // Replace the save button with an edit button
          swapProfileButtons('save');

          // Reenable the submit cart button, if present  (Again: using querySelectorAll to gracefully handle missing elements)
          document.querySelectorAll('#submit-cart-button').forEach(button => {
            button.removeAttribute('disabled');
          });

        } else {

          alert(`ERROR: ${profile.error}`);
          // Reenable the save and cancel buttons, so the user can try again
          saveButton.disabled = false;
          cancelButton.disabled = false;

        }

      });

  } else {
    alert('all fields are required');
    // Reenable the save button, so the user can try again
    saveButton.disabled = false;
  }

}


/**
 * Cancel profile edits and restore the original values
 * @param {integer} id - the ID of the profile being edited
 */

function cancelProfile(id) {

  // Disable the save and cancel buttons, so they can't click repeatedly while waiting
  const saveButton = document.querySelector('#save-profile-button');
  saveButton.disabled = true;
  const cancelButton = document.querySelector('#cancel-button');
  cancelButton.disabled = true;

  // Get the profile's original contents via the API
  fetch(`/users/${id}`, {
    method: 'GET'
  })
    .then(response => response.json())
    .then(profile => {

      // If successful, update the page
      if (profile.error == undefined) {

        // Replace the pseudo-form with the retrieved profile contents
        // CITATION: https://stackoverflow.com/a/34913701/15100723
        for (const [fieldName, fieldValue] of Object.entries(profile)) {
          // Replace the contents of each input with its original value, as returned from the API
          const input = document.querySelector(`#${fieldName}`);
          newElement('span', fieldValue, 'value', fieldName, null, input);
        }

        // Replace the save button with an edit button
        swapProfileButtons('save');

        // Reenable the submit cart button, if present  (Again: using querySelectorAll to gracefully handle missing elements)
        document.querySelectorAll('#submit-cart-button').forEach(button => {
          button.removeAttribute('disabled');
        });


      } else {
        alert(`ERROR: ${profile.error}`);

        // Reenable the save and cancel buttons, so the user can try again
        saveButton.disabled = false;
        cancelButton.disabled = false;

      }

    });

}


/**
 * Create a new HTML element with the specified attributes
 * @param {string} element - The type of HTML element to be created
 * @param {string} innerHTML - The inner HTML to be added to the new element
 * @param {string} [cssClass] - A space-delimited list of classes to be added to the new element (optional)
 * @param {string} id - the ID to be added to the element (optional)
 * @param {string} value - the value to be set for the element (optional)
 * @param {object} replaces - the DOM object it should replace (optional)
 * 
 * NOTE: It would also be useful to support adding the event listeners here,
 * but passing a function with an unknown number of parameters is beyond my skills right now.
 */

function newElement(element, innerHTML, cssClass = null, id = null, value = null, replaces = null) {
  const child = document.createElement(element);
  child.innerHTML = innerHTML;
  if (cssClass !== null) {
    cssClass.split(' ').forEach(cssClass => {
      child.classList.add(cssClass);
    });
    if (id !== null) {
      child.id = id;
    }
    if (value !== null) {
      child.value = value;
    }
    if (replaces !== null) {
      replaces.after(child);
      replaces.remove();
    }
  }
  return child;
}


/**
 * Swap the Edit Profile and Save Profile buttons
 * @param {string} from - the button type to be removed, either 'edit' or 'save' in lowercase
 */

function swapProfileButtons(from) {

  // Validate the parameter
  if (from == 'edit' || from == 'save') {

    to = (from == 'edit') ? 'save' : 'edit';

    // Create a new edit or save button
    const oldButton = document.querySelector(`#${from}-profile-button`);
    // CITATION:  https://flaviocopes.com/how-to-uppercase-first-letter-javascript/
    const newButton = newElement('button', `${to.charAt(0).toUpperCase()}${to.slice(1)}`, 'btn btn-link', `${to}-profile-button`);
    newButton.dataset.profile = oldButton.dataset.profile;
    if (to == 'save') {
      newButton.addEventListener('click', () => saveProfile(oldButton.dataset.profile));
    } else {
      newButton.addEventListener('click', () => profileForm(oldButton.dataset.profile));
    }

    // Replace the old button with the new one
    oldButton.after(newButton);
    oldButton.remove();

    // Add or remove the cancel button
    if (to == 'save') {
      const cancelButton = newElement('button', 'Cancel', 'btn btn-link', 'cancel-button');
      cancelButton.addEventListener('click', () => cancelProfile(oldButton.dataset.profile));
      newButton.after(cancelButton);
    } else {
      document.querySelector('#cancel-button').remove();
    }

  }
}