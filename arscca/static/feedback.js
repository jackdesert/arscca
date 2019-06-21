// For ease of installation across many projects, this does not use handlebars
// This also does not require jquery. See http://youmightnotneedjquery.com/

// When calling bindFeedback(), you m
let bindFeedbackLink = (linkId, extraData) => {
    'use strict'
    // CONSTANTS
    const formUrl = 'https://bip.elitecare.com/feedback'
    const introText = 'I want this page to:'
    const confirmationText = 'Thank you for your feedback!'
    const confirmationButtonText = 'Close'
    const divId = 'feedback-div-3278'
    const submitButtonText = 'Send'


    let acceptMessage = () => {
        const activeElements = []

        const closeFeedbackDivs = () => {
            activeElements.forEach((element) => {
                document.body.removeChild(element)
            })
        }

        const displaySuccess = () => {
            intro.innerHTML = confirmationText
            sendButton.innerHTML = confirmationButtonText
            sendButton.removeEventListener('click', sendFeedback)
            sendButton.addEventListener('click', closeFeedbackDivs)
            sendButton.focus()
            holder.removeChild(textarea)
        }

        const textareaClass = 'feedback__textarea'

        const buildFeedbackPayload = (message) => {
            const payload = {'feedback': {'message': message,
                                          'page': window.location.toString()}}

            for (var key in extraData){
                if (extraData.hasOwnProperty(key)){
                    payload.feedback[key] = extraData[key]
                }
            }
            return payload
        }

        const sendFeedback = () => {
            const textareaDiv = document.querySelector(`.${textareaClass}`)
            const textareaValue = textareaDiv.value
            const request = new XMLHttpRequest()
            const payload = buildFeedbackPayload(textareaValue)

            request.open('POST', formUrl, true)
            request.setRequestHeader('Content-Type', 'application/json')


            request.onload = function() {
                if (request.status >= 200 && request.status < 400) {
                    // Success!
                    var resp = request.responseText;
                    displaySuccess()
                } else {
                    debugger
                    // We reached our target server, but it returned an error

                }
            }

            request.onerror = function() {
                debugger
                // There was a connection error of some sort
            }

            request.send(JSON.stringify(payload))
        }

        let overlay = document.createElement('div')
        let holder = document.createElement('div')
        let intro = document.createElement('div')
        let textarea = document.createElement('textarea')
        let sendButton = document.createElement('button')
        let cancelDiv = document.createElement('div')

        overlay.addEventListener('click', closeFeedbackDivs)
        cancelDiv.addEventListener('click', closeFeedbackDivs)
        sendButton.addEventListener('click', sendFeedback)

        overlay.classList.add('feedback__overlay')
        holder.classList.add('feedback')
        intro.classList.add('feedback__text')
        intro.innerHTML = introText
        textarea.classList.add(textareaClass)
        sendButton.classList.add('feedback__submit')
        sendButton.innerHTML = submitButtonText
        cancelDiv.classList.add('feedback__cancel')
        cancelDiv.innerHTML = 'X'

        holder.appendChild(intro)
        holder.appendChild(textarea)
        holder.appendChild(sendButton)
        holder.appendChild(cancelDiv)
        document.body.appendChild(overlay)
        document.body.appendChild(holder)

        activeElements.push(overlay)
        activeElements.push(holder)
        textarea.focus()
    }

    const linkEl = document.getElementById(linkId)


    if (typeof(extraData) !== 'object'){
        extraData = {}
    }

    linkEl.addEventListener('click', acceptMessage)






}
