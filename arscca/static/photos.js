let bindEnlargePhotoOnClick = () => {
    'use strict'

    let photos = document.querySelectorAll('.uploaded-photo')

    let enlargePhoto = (e) => {
        let clickedImageSrc = e.target.getAttribute('src'),
            overlay = document.getElementById('overlay'),
            overlayImage = document.getElementById('overlay__img'),
            body = document.querySelector('body')

        let reducePhoto = () => {
            overlay.classList.remove('active')
            body.classList.remove('no-scroll')
        }

        overlay.classList.add('active')
        overlay.addEventListener('click', reducePhoto)

        // Remove scrollbar from body while modal is displayed
        body.classList.add('no-scroll')
        overlayImage.setAttribute('src', clickedImageSrc)
    }

    for (let photo of photos){
        photo.addEventListener('click', enlargePhoto)
    }

}
