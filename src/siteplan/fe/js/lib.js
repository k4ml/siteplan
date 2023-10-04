import Swal from 'sweetalert2';

function showAlert() {
    return Swal.fire({
      title: 'Info',
      text: 'This just to show js integration. Click OK will bring you to our github page.',
      icon: 'info',
      confirmButtonText: 'OK',
      showCancelButton: true,
    })
}

export { showAlert };
