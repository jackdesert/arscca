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
                    k = 'tr_stripe'
                }

                driver.row_klass = k

                html = template(driver)
                content += html

            })

            target.innerHTML = content
            replaceInfinity()
        },
        replaceInfinity = function(){
            var elements = document.querySelectorAll('td.fastest-time,td.fastest-pax-time')

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
        sortByDriverName = function(){
            sortString('name')
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

        sortByStringAttributeThenByOverallPosition = function(stringAttribute){
            drivers.sort(function(a, b){
                var overallPositionAttribute = 'position_overall',
                    a1 = a[stringAttribute],
                    b1 = b[stringAttribute],
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

        bindHeaders = function(){
            var carClassHeader        = document.getElementById('car-class'),
                fastestTimeHeader     = document.getElementById('fastest-time'),
                positionOverallHeader = document.getElementById('position-overall'),
                positionPaxHeader     = document.getElementById('position-pax'),
                fastestPaxTimeHeader  = document.getElementById('fastest-pax-time'),
                driverNameHeader      = document.getElementById('driver-name'),
                carModelHeader        = document.getElementById('car-model'),
                carNumberHeader       = document.getElementById('car-number'),
                paxFactorHeader       = document.getElementById('pax-factor'),
                bindings = [[carClassHeader,        sortByCarClassThenByOverallPosition],
                            [carNumberHeader,       sortByCarNumber],
                            [fastestTimeHeader,     sortByOverallPosition],
                            [positionOverallHeader, sortByOverallPosition],
                            [driverNameHeader,      sortByDriverName],
                            [carModelHeader,        sortByCarModelThenByOverallPosition],
                            [positionPaxHeader,     sortByPaxPosition],
                            [paxFactorHeader,       sortByPaxFactorThenByOverallPosition],
                            [fastestPaxTimeHeader,  sortByPaxPosition]]

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
    styleActiveHeader(document.getElementById('fastest-time'))

}
