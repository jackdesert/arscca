// Import for side effects only
import './common'

// Import default export
import initializeDriversTable from './initializeDriversTable'

// Declare this variable (set in templates/layout.jinja2)
declare let ARSCCA_GLOBALS:Record<string, boolean>

initializeDriversTable(ARSCCA_GLOBALS.live)

