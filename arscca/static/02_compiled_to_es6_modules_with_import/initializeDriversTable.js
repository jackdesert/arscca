// var used here because some browsers throw error if "let" used outside of strict context
console.log('Not seeing your changes? Make sure you transpile!');
// How do we get type declarations for this?
//import Vue from 'vue/dist/vue'
// If I simply:
//    import Vue from 'vue'
// I get an error in the browser:
//    "You are using the runtime-only build of Vue where the template compiler is not available. Either pre-compile the templates into render functions, or use the compiler-included build."
// Therefore I am importing specifically 'vue/dist/vue',
// which resolves to 'node_modules/vue/dist/vue.js',
// which is the full version of Vue that inclues the compiler
//
// In order to get type declarations when using `import Vue from 'vue.dist.vue'`,
// run this command in the unix terminal:
//     mkdir node_modules/vue/dist/vue
//     cp -r node_modules/vue/types node_modules/vue/dist/vue
import Vue from 'vue/dist/vue';
let initializeDriversTable = (liveBoolean) => {
    'use strict';
    // Most variables can be declared without specifying a type,
    // and typescript will infer a type. No such
    const delimiters = ['${', '}'];
    const hugeNumber = 1000000;
    let currentSortFunction;
    let currentActiveHeader;
    let mySocket;
    let dimmed = false;
    let drivers = JSON.parse(ARSCCA_GLOBALS.drivers_json);
    // vueRevisionStatus is only needed when liveBoolean is true.
    // However, it is initialized even when liveBoolean is false
    // so that TS can infer its type. (We are using noImplicitAny)
    //
    // Allow TS to infer type on vueRevisionStatus.
    // Otherwise it will complain when you access vueRevisionStatus.currentRevision directly
    let vueRevisionStatus = new Vue({
        delimiters: delimiters,
        el: '#current-revision',
        data: {
            currentRevision: -1,
            timestampOffsetMS: 0,
            timestamp: '1970-01-01T00:00:00.000000',
            now: new Date()
        },
        methods: {
            timestampAgo: function () {
                const that = this, then = Date.parse(that.timestamp), deltaMS = that.now - then - that.timestampOffsetMS, deltaS = deltaMS / 1000, deltaM = deltaS / 60;
                // absolute value so that it doesn't start counting from -0.0
                return Math.abs(deltaM).toFixed(1);
            }
        }
    });
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
            visible: function (driverId) {
                let that = this;
                if (!that.solo) {
                    return true;
                }
                if (that.selectedDriverIds.includes(driverId)) {
                    return true;
                }
                return false;
            },
            replaceInfinity: function (value) {
                if (value === 'Infinity') {
                    return '-';
                }
                return value;
            },
            rowKlass: function (driverId, rowIndex) {
                let that = this;
                if (that.solo) {
                    return this.rowKlassWhenSolo(driverId);
                }
                let klass = '';
                if (that.selectedDriverIds.includes(driverId)) {
                    klass = 'selected';
                }
                if (rowIndex % 2 === 1) {
                    klass += ' tr_stripe';
                }
                return klass;
            },
            rowKlassWhenSolo: function (driverId) {
                // This function decides whether this row should be striped
                // among its peers of other selected drivers
                //
                // WARNING: This runs in N*M time
                // where N is number of drivers and M is number of selected rows
                let stripe = false, that = this;
                for (let driver of that.drivers) {
                    if (that.selectedDriverIds.includes(driver.id)) {
                        stripe = !stripe;
                    }
                    if (driverId === driver.id) {
                        return stripe ? 'selected tr_stripe' : 'selected';
                    }
                }
            },
            toggleSolo: function () {
                let that = this;
                if (!that.solo && (that.selectedDriverIds.length === 0)) {
                    alert('Please select one or more rows first');
                    return;
                }
                that.solo = !that.solo;
            },
            highlightRow: function (driverId) {
                let that = this, index = that.selectedDriverIds.indexOf(driverId), sourceElem = event.srcElement;
                if (sourceElem.href) {
                    // Do not highlight if the clicked element was a link
                    return;
                }
                if (that.solo) {
                    return;
                }
                if (index === -1) {
                    that.selectedDriverIds.push(driverId);
                }
                else {
                    that.selectedDriverIds.splice(index, 1);
                }
            },
            soloButtonKlass: function () {
                let that = this;
                if (that.solo) {
                    return 'solo-button solo-button_active';
                }
                else {
                    return 'solo-button';
                }
            }
        }
    });
    let target = document.getElementById('drivers-tbody'), sortByCarModel = function () {
        sortString('car_model');
    }, sortByCarNumber = function () {
        sortNumeric('car_number');
    }, sortByCodriverCarNumber = function () {
        sortParsedInteger('codriver_car_number');
    }, sortByDriverLastName = function () {
        drivers.sort(function (a, b) {
            let lastNameFirstA = a.name.toLowerCase().split(' ').reverse().join(), lastNameFirstB = b.name.toLowerCase().split(' ').reverse().join();
            if (lastNameFirstA === lastNameFirstB) {
                return 0;
            }
            else if (lastNameFirstA > lastNameFirstB) {
                return 1;
            }
            else {
                return -1;
            }
        });
    }, sortByPaxPosition = function () {
        sortNumeric('secondary_rank');
    }, sortByOverallPosition = function () {
        sortNumeric('primary_rank');
    }, sortNumeric = function (attribute) {
        drivers.sort(function (a, b) {
            let aa = a[attribute], bb = b[attribute];
            if (!aa) {
                aa = hugeNumber;
            }
            if (!bb) {
                bb = hugeNumber;
            }
            return aa - bb;
        });
    }, sortParsedInteger = function (attribute) {
        let regex = /\[|\]/g;
        drivers.sort(function (a, b) {
            let aa = a[attribute] || '', bb = b[attribute] || '', aaa = parseInt(aa.replace(regex, '')) || hugeNumber, bbb = parseInt(bb.replace(regex, '')) || hugeNumber;
            return aaa - bbb;
        });
    }, 
    // Note the numericAttribute is a string (like 'car_year') that **references** a numeric
    sortByNumericThenByString = function (numericAttribute, stringAttribute) {
        drivers.sort(function (a, b) {
            let a_number = parseFloat(a[numericAttribute]) || hugeNumber;
            let b_number = parseFloat(b[numericAttribute]) || hugeNumber;
            let a_string_lower = a[stringAttribute].toLowerCase();
            let b_string_lower = b[stringAttribute].toLowerCase();
            // Compare numeric
            if (a_number > b_number) {
                return 1;
            }
            else if (a_number < b_number) {
                return -1;
            }
            // If numeric was equal, compare string
            if (a_string_lower === b_string_lower) {
                return 0;
            }
            else if (a_string_lower > b_string_lower) {
                return 1;
            }
            else {
                return -1;
            }
        });
    }, sortString = function (attribute) {
        drivers.sort(function (a, b) {
            let aa = a[attribute].toLowerCase(), bb = b[attribute].toLowerCase();
            if (aa === bb) {
                return 0;
            }
            else if (aa > bb) {
                return 1;
            }
            else {
                return -1;
            }
        });
    }, sortByStringAttributeThenByOverallPosition = function (stringAttribute) {
        drivers.sort(function (a, b) {
            let overallPositionAttribute = 'primary_rank', a1 = a[stringAttribute].toLowerCase(), b1 = b[stringAttribute].toLowerCase(), a2 = a[overallPositionAttribute], b2 = b[overallPositionAttribute];
            if (a1 > b1) {
                return 1;
            }
            else if (a1 < b1) {
                return -1;
            }
            // If you made it to here, a1 === b1
            return a2 - b2;
        });
    }, sortByCarClassThenByOverallPosition = function () {
        sortByStringAttributeThenByOverallPosition('car_class');
    }, sortByCarYearThenByCarModel = function () {
        sortByNumericThenByString('car_year', 'car_model');
    }, sortByCarModelThenByOverallPosition = function () {
        sortByStringAttributeThenByOverallPosition('car_model');
    }, sortByPaxFactorThenByOverallPosition = function () {
        sortByStringAttributeThenByOverallPosition('pax_factor');
    }, sortByClassPositionThenByOverallPosition = function () {
        drivers.sort(function (a, b) {
            let A = a.class_rank * hugeNumber + a.primary_rank, B = b.class_rank * hugeNumber + b.primary_rank;
            return A - B;
        });
    }, bindHeaders = function () {
        let carClassHeader = document.getElementById('car-class'), bestCombinedHeader = document.getElementById('best-combined'), positionOverallHeader = document.getElementById('primary-rank'), positionPercentileHeader = document.getElementById('percentile-rank'), positionPaxHeader = document.getElementById('secondary-rank'), positionClassHeader = document.getElementById('class-rank'), bestCombinedPaxHeader = document.getElementById('best-combined-pax'), driverNameHeader = document.getElementById('driver-name'), carYearHeader = document.getElementById('car-year'), carModelHeader = document.getElementById('car-model'), codriverCarNumberHeader = document.getElementById('codriver-car-number'), carNumberHeader = document.getElementById('car-number'), paxFactorHeader = document.getElementById('pax-factor'), bindings = [
            [carClassHeader, sortByCarClassThenByOverallPosition],
            [carNumberHeader, sortByCarNumber],
            [codriverCarNumberHeader, sortByCodriverCarNumber],
            [bestCombinedHeader, sortByOverallPosition],
            [positionOverallHeader, sortByOverallPosition],
            [positionPercentileHeader, sortByOverallPosition],
            [positionPaxHeader, sortByPaxPosition],
            [positionClassHeader, sortByClassPositionThenByOverallPosition],
            [driverNameHeader, sortByDriverLastName],
            [carYearHeader, sortByCarYearThenByCarModel],
            [carModelHeader, sortByCarModelThenByOverallPosition],
            [paxFactorHeader, sortByPaxFactorThenByOverallPosition],
            [bestCombinedPaxHeader, sortByPaxPosition]
        ];
        bindings.forEach(function (array) {
            let header = array[0], func = array[1], headerAsElement = header;
            if (header === null) {
                console.log('WARNING: no header for func', func);
                return;
            }
            headerAsElement.addEventListener('click', function () {
                let that = this;
                // Store which sort function most recently selected
                currentSortFunction = func;
                currentSortFunction();
                currentActiveHeader = that;
                styleActiveHeader(that);
            });
        });
    }, styleActiveHeader = function (activeElement) {
        let sortableHeaderClass = 'sortable-header', activeHeaderClass = 'sortable-header_active', cellHighlightClass = 'td_active-sort', cellClassToHighlight = activeElement.id;
        // Header
        document.querySelectorAll('.' + sortableHeaderClass).forEach(function (element) {
            element.classList.remove(activeHeaderClass);
        });
        activeElement.classList.add(activeHeaderClass);
        // Columns
        document.querySelectorAll('td').forEach(function (element) {
            element.classList.remove(cellHighlightClass);
        });
        document.querySelectorAll('.' + cellClassToHighlight).forEach(function (element) {
            element.classList.add(cellHighlightClass);
        });
    }, fetchLiveDriversAndKickoff = function () {
        const request = new XMLHttpRequest();
        request.open('GET', '/live/drivers', true);
        request.onload = function () {
            if (this.status >= 200 && this.status < 400) {
                // Success!
                const data = JSON.parse(this.response), requestTimestamp = Date.parse(data.request_timestamp);
                // Remove all drivers from array
                drivers.splice(0);
                data.drivers.forEach(function (row) {
                    drivers.push(row);
                });
                vueRevisionStatus.currentRevision = data.revision;
                vueRevisionStatus.timestamp = data.revision_timestamp;
                vueRevisionStatus.timestampOffsetMS = new Date() - requestTimestamp;
                kickoff();
            }
            else {
                // We reached our target server, but it returned an error
                console.log(`status ${this.status} fetching drivers`);
            }
        };
        request.onerror = function () {
            console.log('error fetching live drivers');
        };
        request.send();
    }, kickoff = function () {
        // Apply the most recently selected sort function
        currentSortFunction();
        // These next methods are called with setTimeout
        // so the view can populate before it takes action
        // I wonder if slow devices will need more than the token 1 ms
        setTimeout(function () {
            styleActiveHeader(currentActiveHeader);
        }, 1);
        if (liveBoolean) {
            setTimeout(initializeWebsocket, 1000);
        }
    }, driverIndexFromName = function (name) {
        const index = drivers.findIndex(function (item) {
            return item.name === name;
        });
        return index;
    }, processWebsocketMessage = function (event) {
        const messageData = JSON.parse(event.data), revision = messageData.revision, revisionTimestamp = messageData.revision_timestamp, driverChanges = messageData.driver_changes, removeDriver = function (name) {
            const index = driverIndexFromName(name);
            console.log('Deleting driver: ', name);
            // Use splice to delete driver
            drivers.splice(index, 1);
        }, addDriver = function (name) {
            console.log('Adding driver: ', name);
            // Name is all that is needed
            drivers.push({ name: name, class_rank: -1000, primary_rank: -1000 });
        }, updateDriver = function (driverObject) {
            // Note that if a driver is removed,
            // "primary_rank" will change for any
            // slower drivers, and hence they will be updated
            const index = driverIndexFromName(driverObject.name);
            console.log('Updating driver: ', driverObject);
            Vue.set(drivers, index, driverObject);
        };
        if (!revision) {
            console.log('ERROR: No revision in message');
        }
        console.log('Message received: ', revision);
        if (revision <= vueRevisionStatus.currentRevision) {
            console.log(`skipping revision ${revision} because currentRevision is ${vueRevisionStatus.currentRevision}`);
        }
        else if (revision === vueRevisionStatus.currentRevision + 1) {
            vueRevisionStatus.currentRevision = revision;
            vueRevisionStatus.timestamp = revisionTimestamp;
            driverChanges.create.forEach(addDriver);
            driverChanges.destroy.forEach(removeDriver);
            driverChanges.update.forEach(updateDriver);
            // apply sorting
            currentSortFunction();
            // re-bind clickDriverRow
            dimScreen();
        }
        else {
            // Close socket and start over
            console.log(`Closing socket and starting over because revision ${revision} vs currentRevision ${vueRevisionStatus.currentRevision}`);
            mySocket.close();
            fetchLiveDriversAndKickoff();
        }
    }, initializeWebsocketSoon = function () {
        setTimeout(initializeWebsocket, 1000);
    }, initializeWebsocket = function () {
        const printConnectionState = function () {
            const element = document.getElementById('connection-state'), stateInteger = mySocket.readyState, labels = ['0  CONNECTING  Socket has been created. The connection is not yet open.',
                '1  OPEN  The connection is open and ready to communicate.',
                '2  CLOSING   The connection is in the process of closing.',
                '3  CLOSED  The connection is closed or could not be opened.'];
            element.textContent = labels[stateInteger];
            // Long delay so we can actually read the inital state before the div changes
            setTimeout(printConnectionState, 400);
        }, hostname = window.location.hostname;
        if (liveBoolean) {
            // create websocket instance
            mySocket = new WebSocket(`ws://${hostname}:6544/ws`);
            mySocket.onmessage = processWebsocketMessage;
            mySocket.onclose = initializeWebsocketSoon;
            printConnectionState();
        }
    }, dimScreen = function () {
        const body = document.getElementById('body'), dimKlass = 'body_dimmed', unDimScreen = function () {
            dimmed = false;
            body.classList.remove(dimKlass);
        };
        if (!dimmed) {
            body.classList.add(dimKlass);
            dimmed = true;
            setTimeout(unDimScreen, 600);
        }
    }, updateTimeAgo = function () {
        vueRevisionStatus.now = new Date();
        setTimeout(updateTimeAgo, 6000);
    };
    // Specify initial sort
    currentSortFunction = sortByOverallPosition;
    currentActiveHeader = document.getElementById('best-combined');
    bindHeaders();
    if (liveBoolean) {
        fetchLiveDriversAndKickoff();
        updateTimeAgo();
    }
    else {
        kickoff();
    }
};
export default initializeDriversTable;
