import Swal from 'sweetalert2';

document.addEventListener('DOMContentLoaded', () => {
  const showSweetAlertButton = document.getElementById('showSweetAlertButton');

  if (showSweetAlertButton) {
    showSweetAlertButton.addEventListener('click', () => {
      Swal.fire({
        title: 'Confirm Action',
        text: 'Do you want to proceed with this action?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel'
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire(
            'Confirmed!',
            'Your action has been confirmed.',
            'success'
          );
        } else if (result.dismiss === Swal.DismissReason.cancel) {
          Swal.fire(
            'Cancelled',
            'Your action has been cancelled.',
            'error'
          );
        }
      });
    });
  }
});