document.addEventListener('DOMContentLoaded', function () {
    const changePictureBtn = document.querySelector('.btn-change-picture');
    const pictureInput = document.querySelector('#profilePictureInput');
    const previewImg = document.querySelector('#profilePreview');
    const form = document.querySelector('.profile-form');
    const saveModal = document.querySelector('#saveModal');
    const closeModalBtn = document.querySelector('#closeModal');
    const avatarOverlay = document.querySelector('.avatar-overlay');

    if (changePictureBtn && pictureInput && previewImg && form) {
        changePictureBtn.addEventListener('click', function () {
            pictureInput.click();
        });

        if (avatarOverlay) {
            avatarOverlay.addEventListener('click', function () {
                pictureInput.click();
            });
        }

        pictureInput.addEventListener('change', function () {
            if (pictureInput.files.length > 0) {
                const file = pictureInput.files[0];
                const reader = new FileReader();

                reader.onload = function (e) {
                    previewImg.src = e.target.result;
                    changePictureBtn.innerHTML = `<i class="fas fa-camera me-1"></i> ${file.name.substring(0, 20)}${file.name.length > 20 ? '...' : ''}`;
                };

                reader.readAsDataURL(file);
            } else {
                previewImg.src = document.querySelector('[data-original-src]')?.getAttribute('data-original-src') || '/static/img/user.webp';
                changePictureBtn.innerHTML = `<i class="fas fa-camera me-1"></i> Cambiar foto de perfil`;
            }
        });

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (saveModal) {
                saveModal.classList.add('show');
            }
            setTimeout(() => {
                form.submit();
            }, 1800);
        });

        if (closeModalBtn && saveModal) {
            closeModalBtn.addEventListener('click', function () {
                saveModal.classList.remove('show');
            });
        }
    }
});