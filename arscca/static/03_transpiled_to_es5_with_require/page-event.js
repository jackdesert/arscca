'use strict';

require('./common');

var _initializeDriversTable = require('./initializeDriversTable');

var _initializeDriversTable2 = _interopRequireDefault(_initializeDriversTable);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

// Import for side effects only
(0, _initializeDriversTable2.default)(ARSCCA_GLOBALS.live);
// Import default export