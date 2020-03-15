'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
var initializePhotosPage = function initializePhotosPage() {
    var bindEnlargePhotoOnClick = function bindEnlargePhotoOnClick() {
        'use strict';

        var photos = document.querySelectorAll('.uploaded-photo');
        var enlargePhoto = function enlargePhoto(e) {
            var clickedImageSrc = e.target.getAttribute('src'),
                overlay = document.getElementById('overlay'),
                overlayImage = document.getElementById('overlay__img'),
                body = document.querySelector('body');
            var reducePhoto = function reducePhoto() {
                overlay.classList.remove('active');
                body.classList.remove('no-scroll');
            };
            overlayImage.setAttribute('src', clickedImageSrc);
            overlay.classList.add('active');
            // Remove scrollbar from body while modal is displayed
            body.classList.add('no-scroll');
            // There are two ways to call reducePhoto
            // 1. Click on the enlarged photo
            // 2. Click the back button in the browser
            //
            // This sets up item #1
            overlay.addEventListener('click', reducePhoto);
            //
            // This sets up item #2
            history.pushState({}, 'Enlarged Image', '#i');
            window.addEventListener('popstate', reducePhoto);
        };
        var _iteratorNormalCompletion = true;
        var _didIteratorError = false;
        var _iteratorError = undefined;

        try {
            for (var _iterator = photos[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                var photo = _step.value;

                photo.addEventListener('click', enlargePhoto);
            }
        } catch (err) {
            _didIteratorError = true;
            _iteratorError = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion && _iterator.return) {
                    _iterator.return();
                }
            } finally {
                if (_didIteratorError) {
                    throw _iteratorError;
                }
            }
        }
    };
    var bindGroupPhotosByRadioButtons = function bindGroupPhotosByRadioButtons() {
        'use strict';

        var byUploadDate = document.getElementById('group-by-upload-date');
        var bySnapDate = document.getElementById('group-by-snap-date');
        byUploadDate.addEventListener('click', function () {
            window.location = '/photos?g=1';
        });
        bySnapDate.addEventListener('click', function () {
            window.location = '/photos';
        });
    };
    bindEnlargePhotoOnClick();
    bindGroupPhotosByRadioButtons();
};
exports.default = initializePhotosPage;