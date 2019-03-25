var initializeDriversTable = function(){
    'use strict'

    var templateSource = document.getElementById('driver-template').innerHTML,
        template = Handlebars.compile(templateSource),
        target = document.getElementById('drivers-tbody'),
        displayDrivers = function(){
            var content = '',
                html

            drivers.forEach(function(driver, index){
                var k = ''
                if (index % 2 === 0){
                    k = 'tr_stripe '
                }

                driver.row_klass = k

                if (selectedDriverIds.has(driver.id)){
                    driver.row_klass += klassToToggle
                }

                html = template(driver)
                content += html

            })

            target.innerHTML = content
            bindClickDriverRow()
            replaceInfinity()
        },
        replaceInfinity = function(){
            var elements = document.querySelectorAll('td.best-combined,td.best-combined-pax')

            elements.forEach(function(element){
                if(element.textContent === 'Infinity'){
                    element.textContent = '-'
                }
            })

        },
        sortByCarModel = function(){
            sortString('car_model')
        },
        sortByCarNumber = function(){
            sortNumeric('car_number')
        },
        sortByDriverLastName = function(){
            drivers.sort(function(a, b){
                var lastNameFirstA = a.name.toLowerCase().split(' ').reverse().join(),
                    lastNameFirstB = b.name.toLowerCase().split(' ').reverse().join()
                if (lastNameFirstA === lastNameFirstB){
                    return 0
                }else if (lastNameFirstA > lastNameFirstB){
                    return 1
                }else{
                    return -1
                }
            })
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
                var aa = a[attribute].toLowerCase(),
                    bb = b[attribute].toLowerCase()
                if (aa === bb){
                    return 0
                }else if (aa > bb){
                    return 1
                }else{
                    return -1
                }
            })
        },

        sortByStringAttributeThenByOverallPosition = function(stringAttribute){
            drivers.sort(function(a, b){
                var overallPositionAttribute = 'position_overall',
                    a1 = a[stringAttribute].toLowerCase(),
                    b1 = b[stringAttribute].toLowerCase(),
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
        sortByCarClassThenByOverallPosition = function(){
            sortByStringAttributeThenByOverallPosition('car_class')
        },

        sortByCarModelThenByOverallPosition = function(){
            sortByStringAttributeThenByOverallPosition('car_model')
        },

        sortByPaxFactorThenByOverallPosition = function(){
            sortByStringAttributeThenByOverallPosition('pax_factor')
        },

        sortByClassPositionThenByOverallPosition = function(){
            drivers.sort(function(a, b){
                var huge = 1000000,
                    A = a.position_class * huge + a.position_overall,
                    B = b.position_class * huge + b.position_overall
                return A - B
            })
        },

        bindHeaders = function(){
            var carClassHeader        = document.getElementById('car-class'),
                bestCombinedHeader    = document.getElementById('best-combined'),
                positionOverallHeader = document.getElementById('position-overall'),
                positionPaxHeader     = document.getElementById('position-pax'),
                positionClassHeader   = document.getElementById('position-class'),
                bestCombinedPaxHeader  = document.getElementById('best-combined-pax'),
                driverNameHeader      = document.getElementById('driver-name'),
                carModelHeader        = document.getElementById('car-model'),
                carNumberHeader       = document.getElementById('car-number'),
                paxFactorHeader       = document.getElementById('pax-factor'),
                bindings = [
                    [carClassHeader,        sortByCarClassThenByOverallPosition],
                    [carNumberHeader,       sortByCarNumber],
                    [bestCombinedHeader,    sortByOverallPosition],
                    [positionOverallHeader, sortByOverallPosition],
                    [positionPaxHeader,     sortByPaxPosition],
                    [positionClassHeader,   sortByClassPositionThenByOverallPosition],
                    [driverNameHeader,      sortByDriverLastName],
                    [carModelHeader,        sortByCarModelThenByOverallPosition],
                    [paxFactorHeader,       sortByPaxFactorThenByOverallPosition],
                    [bestCombinedPaxHeader, sortByPaxPosition]]

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

        },


        klassToToggle = 'selected',

        selectedDriverIds = new Set(),

        bindClickDriverRow = function(){
            console.log('binding')
            var rows = document.querySelectorAll('tbody tr')


            console.log('rows: ', rows)

            rows.forEach(function(row){
                row.addEventListener('click', function(event){
                    var cellParent = event.target.parentElement,
                        driverId = parseInt(cellParent.id, 10)
                    if (selectedDriverIds.has(driverId)){
                        selectedDriverIds.delete(driverId)
                    }else{
                        selectedDriverIds.add(driverId)
                    }

                    cellParent.classList.toggle(klassToToggle)
                })

            })

        }




    sortByOverallPosition()
    displayDrivers()
    bindHeaders()
    styleActiveHeader(document.getElementById('best-combined'))

}
