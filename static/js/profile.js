document.addEventListener('DOMContentLoaded', function () {
    const changePictureBtn = document.querySelector('.btn-change-picture');
    const pictureInput = document.querySelector('#profilePictureInput');
    const previewImg = document.querySelector('#profilePreview');
    const form = document.querySelector('.profile-form-content');

    if (changePictureBtn && pictureInput && previewImg && form) {
        changePictureBtn.addEventListener('click', function () {
            pictureInput.click();
        });

        pictureInput.addEventListener('change', function () {
            if (pictureInput.files.length > 0) {
                const file = pictureInput.files[0];
                const reader = new FileReader();

                reader.onload = function (e) {
                    previewImg.src = e.target.result; 
                };

                reader.readAsDataURL(file);
                changePictureBtn.innerHTML = `<i class="fas fa-camera me-1"></i> ${file.name}`;
            } else {
                previewImg.src = '{% if request.user.profile_picture %}{{ request.user.profile_picture.url }}{% else %}{% static "img/user.webp" %}{% endif %}';
                changePictureBtn.innerHTML = `<i class="fas fa-camera me-1"></i> Cambiar foto de perfil`;
            }
        });

        form.addEventListener('submit', function (e) {
            setTimeout(() => {
                if (request.user.profile_picture) {
                    previewImg.src = '{{ request.user.profile_picture.url }}'.replace(/\/\/+/g, '/'); // Actualizar con URL de S3
                } else {
                    previewImg.src = '{% static "img/user.webp" %}';
                }
            }, 100); 
        });
    }
});