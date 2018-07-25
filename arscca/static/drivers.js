var initializeDriversTable = function(){
    'use strict'

    var templateSource = document.getElementById('driver-template').innerHTML,
        template = Handlebars.compile(templateSource),
        target = document.getElementById('drivers-tbody'),
        displayDrivers = function(){
            var content = '',
                html

            drivers.forEach(function(driver){

                html = template(driver)
                content += html

            })

            target.innerHTML = content
        },
        sortByPaxPosition = function(){
            sortNumeric('position_pax')
        },
        sortByOverallPosition = function(){
            sortNumeric('position_overall')
        },
        sortNumeric = function(attribute){
            drivers.sort(function(a, b){ return a[attribute] - b[attribute] })
        },
        sortString = function(attribute){
            drivers.sort(function(a, b){
                var aa = a[attribute],
                    bb = b[attribute]
                if (aa === bb){
                    return 0
                }else if (aa > bb){
                    return 1
                }else{
                    return -1
                }
            })
        },

        sortByCarClass = function(){
            drivers.sort(function(a, b){
                var carClassAttribute = 'car_class',
                    overallPositionAttribute = 'position_overall',
                    a1 = a[carClassAttribute],
                    b1 = b[carClassAttribute],
                    a2 = a[overallPositionAttribute],
                    b2 = b[overallPositionAttribute]
                if(a1 > b1){
                    return 1
                }else if (a1 < b1){
                    return -1
                }
                // If you made it to here, a1 === b1
                return a2 - b2
            })
        },
        bindHeaders = function(){
            var carClassHeader = document.getElementById('car-class'),
                fastestTimeHeader = document.getElementById('fastest-time'),
                fastestPaxTimeHeader = document.getElementById('fastest-pax-time'),
                bindings = [[carClassHeader, sortByCarClass],
                            [fastestTimeHeader, sortByOverallPosition],
                            [fastestPaxTimeHeader, sortByPaxPosition]]

            bindings.forEach(function(array){
                var header = array[0],
                    func = array[1]
                header.addEventListener('click', function(){
                    var that = this
                    func()
                    displayDrivers()
                    styleActiveHeader(that)
                })
            })
        },

        styleActiveHeader = function(activeElement){
            var sortableHeaderClass = 'sortable-header',
                activeHeaderClass = 'sortable-header_active',
                cellHighlightClass = 'td_active-sort',
                cellClassToHighlight = activeElement.id


            // Header
            document.querySelectorAll('.' + sortableHeaderClass).forEach(function(element){
                element.classList.remove(activeHeaderClass)
            })
            activeElement.classList.add(activeHeaderClass)


            // Columns
            document.querySelectorAll('td').forEach(function(element){
                element.classList.remove(cellHighlightClass)
            })

            document.querySelectorAll('.' + cellClassToHighlight).forEach(function(element){
                element.classList.add(cellHighlightClass)
            })

        }




    sortByOverallPosition()
    displayDrivers()
    bindHeaders()

}
