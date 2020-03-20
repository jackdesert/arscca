// var used here because some browsers throw error if "let" used outside of strict context
console.log('Not seeing your changes? Make sure you transpile!')
interface Driver {
  name:string,
  class_rank:number,
  primary_rank:number
}


declare var drivers:[Driver]

// Hopefully this picks up the correct (ES6) version of Vue
import Vue from 'vue/dist/vue'

let initializeDriversTable = (liveBoolean) =>{
    'use strict'

    const hugeNumber:number = 1000000
    const delimiters:any = ['${', '}']

    let currentSortFunction: Function
    let currentActiveHeader
    let mySocket: Websocket
    let dimmed: boolean = false

    //var templateSource = document.getElementById('driver-template').innerHTML,
    //var template = Handlebars.compile(templateSource),


    let vueRevisionStatus: Vue
    if (liveBoolean){

        vueRevisionStatus = new Vue({
            delimiters: delimiters,
            el: '#current-revision',
            data: {
                currentRevision: -1,
                timestampOffsetMS: 0,
                timestamp: '1970-01-01T00:00:00.000000',
                now: new Date() as Date
            },
            methods:{
                timestampAgo: function(event){
                    const then = Date.parse(this.timestamp),
                        deltaMS = this.now - then - this.timestampOffsetMS,
                        deltaS = deltaMS / 1000,
                        deltaM = deltaS / 60
                    // absolute value so that it doesn't start counting from -0.0
                    return Math.abs(deltaM).toFixed(1)
                }
            }
        })


    }

    const vueDriversTable = new Vue({
        delimiters: delimiters,
        el: '#drivers-table-holder',
        data: {
            drivers: drivers,
            // selectedDriverIds is an array, not a new Set()
            // because Vue knows how to be reactive to changes in an array
            selectedDriverIds: [],
            solo: false
        },
        methods: {
            visible: function(driverId){
                if (!this.solo){
                    return true
                }

                if (this.selectedDriverIds.includes(driverId)){
                    return true
                }

                return false
            },
            replaceInfinity: function(value){
                if(value === 'Infinity'){
                    return '-'
                }
                return value
            },
            rowKlass: function(driverId, rowIndex){
                if (this.solo){
                    return this.rowKlassWhenSolo(driverId)
                }

                let klass = ''
                if (this.selectedDriverIds.includes(driverId)){
                    klass = 'selected'
                }
                if (rowIndex % 2 === 1){
                    klass += ' tr_stripe'
                }
                return klass
            },
            rowKlassWhenSolo: function(driverId){
                // This function decides whether this row should be striped
                // among its peers of other selected drivers
                //
                // WARNING: This runs in N*M time
                // where N is number of drivers and M is number of selected rows
                let stripe = false
                for (let driver of this.drivers){
                    if (this.selectedDriverIds.includes(driver.id)){
                        stripe = !stripe
                    }
                    if (driverId === driver.id){
                        return stripe ? 'selected tr_stripe' : 'selected'
                    }
                }
            },
            toggleSolo: function(){
                if (!this.solo && (this.selectedDriverIds.length === 0)){
                    alert('Please select one or more rows first')
                    return
                }

                this.solo = !this.solo

            },
            highlightRow: function(driverId){
                let index = this.selectedDriverIds.indexOf(driverId)

                if (this.event.srcElement.href){
                    // Do not highlight if the clicked element was a link
                    return
                }
                if (this.solo){
                    return
                }

                if (index === -1){
                    this.selectedDriverIds.push(driverId)
                }else{
                    this.selectedDriverIds.splice(index, 1)
                }
            },
            soloButtonKlass: function(){
                if (this.solo){
                    return 'solo-button solo-button_active'
                }else{
                    return 'solo-button'
                }
            }
        }
    })

    var target = document.getElementById('drivers-tbody'),
        sortByCarModel = function(){
            sortString('car_model')
        },
        sortByCarNumber = function(){
            sortNumeric('car_number')
        },
        sortByCodriverCarNumber = function(){
            sortParsedInteger('codriver_car_number')
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
            sortNumeric('secondary_rank')
        },
        sortByOverallPosition = function(){
            sortNumeric('primary_rank')
        },
        sortNumeric = function(attribute){
            drivers.sort(function(a, b){
                var aa = a[attribute],
                    bb = b[attribute]
                if (!aa){ aa = hugeNumber }
                if (!bb){ bb = hugeNumber }
                return aa - bb
            })
        },
        sortParsedInteger = function(attribute){
            var regex = /\[|\]/g
            drivers.sort(function(a, b){
                var aa = a[attribute] || '',
                    bb = b[attribute] || ''

                aa = parseInt(aa.replace(regex, '')) || hugeNumber
                bb = parseInt(bb.replace(regex, '')) || hugeNumber

                return aa - bb
            })
        },
        sortByNumericThenByString = function(numericAttribute, stringAttribute){
            drivers.sort(function(a, b){
                var a_number = parseFloat(a[numericAttribute]) || hugeNumber
                var b_number = parseFloat(b[numericAttribute]) || hugeNumber
                var a_string_lower = a[stringAttribute].toLowerCase()
                var b_string_lower = b[stringAttribute].toLowerCase()


                // Compare numeric
                if(a_number > b_number){
                    return 1
                }else if(a_number < b_number){
                    return -1
                }

                // If numeric was equal, compare string
                if (a_string_lower === b_string_lower){
                    return 0
                }else if (a_string_lower > b_string_lower){
                    return 1
                }else{
                    return -1
                }
            })
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
                var overallPositionAttribute = 'primary_rank',
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

        sortByCarYearThenByCarModel = function(){
            sortByNumericThenByString('car_year', 'car_model')
        },
        sortByCarModelThenByOverallPosition = function(){
            sortByStringAttributeThenByOverallPosition('car_model')
        },

        sortByPaxFactorThenByOverallPosition = function(){
            sortByStringAttributeThenByOverallPosition('pax_factor')
        },

        sortByClassPositionThenByOverallPosition = function(){
            drivers.sort(function(a, b){
                var A = a.class_rank * hugeNumber + a.primary_rank,
                    B = b.class_rank * hugeNumber + b.primary_rank
                return A - B
            })
        },

        bindHeaders = function(){
            var carClassHeader        = document.getElementById('car-class'),
                bestCombinedHeader    = document.getElementById('best-combined'),
                positionOverallHeader = document.getElementById('primary-rank'),
                positionPaxHeader     = document.getElementById('secondary-rank'),
                positionClassHeader   = document.getElementById('class-rank'),
                bestCombinedPaxHeader = document.getElementById('best-combined-pax'),
                driverNameHeader      = document.getElementById('driver-name'),
                carYearHeader         = document.getElementById('car-year'),
                carModelHeader        = document.getElementById('car-model'),
                codriverCarNumberHeader  = document.getElementById('codriver-car-number'),
                carNumberHeader       = document.getElementById('car-number'),
                paxFactorHeader       = document.getElementById('pax-factor'),
                bindings = [
                    [carClassHeader,        sortByCarClassThenByOverallPosition],
                    [carNumberHeader,       sortByCarNumber],
                    [codriverCarNumberHeader,     sortByCodriverCarNumber],
                    [bestCombinedHeader,    sortByOverallPosition],
                    [positionOverallHeader, sortByOverallPosition],
                    [positionPaxHeader,     sortByPaxPosition],
                    [positionClassHeader,   sortByClassPositionThenByOverallPosition],
                    [driverNameHeader,      sortByDriverLastName],
                    [carYearHeader,         sortByCarYearThenByCarModel],
                    [carModelHeader,        sortByCarModelThenByOverallPosition],
                    [paxFactorHeader,       sortByPaxFactorThenByOverallPosition],
                    [bestCombinedPaxHeader, sortByPaxPosition]]

            bindings.forEach(function(array){
                var header = array[0],
                    func = array[1],
                    headerAsElement = header as HTMLInputElement
                if(header === null){
                    console.log('WARNING: no header for func', func)
                    return
                }
                headerAsElement.addEventListener('click', function(){
                    var that = this
                    // Store which sort function most recently selected
                    currentSortFunction = func
                    currentSortFunction()


                    currentActiveHeader = that
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


        fetchLiveDriversAndKickoff = function(){
            const request = new XMLHttpRequest()
            request.open('GET', '/live/drivers', true)

            request.onload = function() {
                if (this.status >= 200 && this.status < 400) {
                    // Success!
                    const data = JSON.parse(this.response),
                        requestTimestamp = Date.parse(data.request_timestamp)
                    // Remove all drivers from array
                    drivers.splice(0)
                    data.drivers.forEach(function(row){
                        drivers.push(row)
                    })

                    vueRevisionStatus.currentRevision = data.revision
                    vueRevisionStatus.timestamp = data.revision_timestamp
                    vueRevisionStatus.timestampOffsetMS = new Date() as Date - requestTimestamp as Date
                    kickoff()
                } else {
                    // We reached our target server, but it returned an error
                    console.log(`status ${this.status} fetching drivers`)
                }
            }

            request.onerror = function() {
                console.log('error fetching live drivers')
            }

            request.send()



        },

        kickoff = function(){
            // Apply the most recently selected sort function
            currentSortFunction()

            // These next methods are called with setTimeout
            // so the view can populate before it takes action
            // I wonder if slow devices will need more than the token 1 ms
            setTimeout(function(){
                styleActiveHeader(currentActiveHeader)
            }, 1)

            setTimeout(initializeWebsocket, 1000)
        },

        driverIndexFromName = function(name: string){
            const index: number = drivers.findIndex(function(item: Driver){
                return item.name === name
            })

            return index
        },

        processWebsocketMessage = function(event: Event){
            const messageData = JSON.parse(event.data),
                revision = messageData.revision,
                revisionTimestamp = messageData.revision_timestamp,
                driverChanges = messageData.driver_changes,
                removeDriver = function(name: string){
                    const index = driverIndexFromName(name)
                    console.log('Deleting driver: ', name)
                    // Use splice to delete driver
                    drivers.splice(index, 1)
                },
                addDriver = function(name: string){
                    console.log('Adding driver: ', name)
                    // Name is all that is needed
                    drivers.push({name: name, class_rank: -1000, primary_rank: -1000 })
                },
                updateDriver = function(driverObject: Driver){
                    // Note that if a driver is removed,
                    // "primary_rank" will change for any
                    // slower drivers, and hence they will be updated

                    const index = driverIndexFromName(driverObject.name)

                    console.log('Updating driver: ', driverObject)
                    Vue.set(drivers, index, driverObject)
                }

            if (!revision){
                console.log('ERROR: No revision in message')
            }

            console.log('Message received: ', revision)

            if (revision <= vueRevisionStatus.currentRevision){
                console.log(`skipping revision ${revision} because currentRevision is ${vueRevisionStatus.currentRevision}`)
            }else if (revision === vueRevisionStatus.currentRevision + 1){
                vueRevisionStatus.currentRevision = revision
                vueRevisionStatus.timestamp = revisionTimestamp

                driverChanges.create.forEach(addDriver)
                driverChanges.destroy.forEach(removeDriver)
                driverChanges.update.forEach(updateDriver)
                // apply sorting
                currentSortFunction()
                // re-bind clickDriverRow
                dimScreen()

            }else{
                // Close socket and start over
                console.log(`Closing socket and starting over because revision ${revision} vs currentRevision ${vueRevisionStatus.currentRevision}`)
                mySocket.close()
                fetchLiveDriversAndKickoff()
            }
        },

        initializeWebsocketSoon = function(){
            setTimeout(initializeWebsocket, 1000)
        },
        initializeWebsocket = function(){
            const printConnectionState = function(){
                const element = document.getElementById('connection-state'),
                    stateInteger = mySocket.readyState,
                    labels = ['0  CONNECTING  Socket has been created. The connection is not yet open.',
                              '1  OPEN  The connection is open and ready to communicate.',
                              '2  CLOSING   The connection is in the process of closing.',
                              '3  CLOSED  The connection is closed or could not be opened.']



                element.textContent = labels[stateInteger]

                // Long delay so we can actually read the inital state before the div changes
                setTimeout(printConnectionState, 400)
            },
            hostname = window.location.hostname

            if (liveBoolean){

                // create websocket instance
                mySocket = new WebSocket(`ws://${hostname}:6544/ws`)

                mySocket.onmessage = processWebsocketMessage
                mySocket.onclose = initializeWebsocketSoon

                printConnectionState()
            }
    },
    dimScreen = function(){
        const body = document.getElementById('body'),
            dimKlass = 'body_dimmed',
            unDimScreen = function(){
                dimmed = false
                body.classList.remove(dimKlass)
            }


        if (!dimmed){
            body.classList.add(dimKlass)
            dimmed = true
            setTimeout(unDimScreen, 600)
        }
    },
    updateTimeAgo = function(){
        vueRevisionStatus.now = new Date()
        setTimeout(updateTimeAgo, 6000)
    }



    // Specify initial sort
    currentSortFunction = sortByOverallPosition
    currentActiveHeader = document.getElementById('best-combined')

    bindHeaders()
    if (liveBoolean){
        fetchLiveDriversAndKickoff()
        updateTimeAgo()
    }else{
        kickoff()
    }

}

export default initializeDriversTable
