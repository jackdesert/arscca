var displayDrivers = function(){

    var templateSource = document.getElementById('driver-template').innerHTML,
        template = Handlebars.compile(templateSource),
        target = document.getElementById('drivers-tbody'),
        content = '',
        html

    drivers.forEach(function(driver){

        html = template(driver)
        console.log(html)
        content += html

    })

    target.innerHTML = content



}
