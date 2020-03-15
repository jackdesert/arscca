let initializePhotosPage = () => {
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

            overlayImage.setAttribute('src', clickedImageSrc)
            overlay.classList.add('active')
            // Remove scrollbar from body while modal is displayed
            body.classList.add('no-scroll')


            // There are two ways to call reducePhoto
            // 1. Click on the enlarged photo
            // 2. Click the back button in the browser
            //
            // This sets up item #1
            overlay.addEventListener('click', reducePhoto)
            //
            // This sets up item #2
            history.pushState({}, 'Enlarged Image', '#i')
            window.addEventListener('popstate', reducePhoto)


        }

        for (let photo of photos ){
            photo.addEventListener('click', enlargePhoto)
        }

    }

    let bindGroupPhotosByRadioButtons = () => {
        'use strict'
        let byUploadDate = document.getElementById('group-by-upload-date')
        let bySnapDate = document.getElementById('group-by-snap-date')

        byUploadDate.addEventListener('click', () => {
            window.location = '/photos?g=1' as any
        })

        bySnapDate.addEventListener('click', () => {
            window.location = '/photos' as any
        })
    }


    bindEnlargePhotoOnClick()
    bindGroupPhotosByRadioButtons()

}

export default initializePhotosPage
