import Swal from 'sweetalert2';
import htmx from 'htmx.org';

function showAlert() {
    return Swal.fire({
      title: 'Info',
      text: 'This just to show js integration. Click OK will bring you to our github page.',
      icon: 'info',
      confirmButtonText: 'OK',
      showCancelButton: true,
    })
}

document.body.addEventListener('htmx:confirm', function(evt) {
    evt.preventDefault();
    Swal.fire({
      title: "Are you sure?",
      text: "Are you sure you are sure?",
      icon: "warning",
      buttons: true,
      dangerMode: true,
    }).then((confirmed) => {
      if (confirmed) {
        evt.detail.issueRequest();
      }
   });
});

export { showAlert, htmx };
