digraph summary{
		is_handheld_on [fontsize=18, style=filled, fillcolor=lightgreen, shape=octagon]


    success [style=filled, fillcolor=lightgreen, fontsize=18]
    verify_axware_barcode_settings [style=filled, fillcolor=pink]
    reset_scanner_and_start_over [style=filled, fillcolor=pink]
    use_python_to_verify_serial_data [style=filled, fillcolor=pink]
    replace_one_or_both_cables [style=filled, fillcolor=pink]

    is_handheld_on -> turn_on_handheld [label="No"]
    turn_on_handheld -> is_handheld_on [label="Try again1"]

    is_barcoding_activated_in_axware -> activate_barcoding_in_axware [label="No"]
    is_axware_set_to_staging -> set_axware_to_staging_mode [label="No"]
    set_axware_to_staging_mode -> is_axware_set_to_staging [label="Retry"]
    does_cable_2_light_up -> is_cable_1_connected [label="No"]
    link_scanner_with_base -> is_scanner_linked [label="Try Again 5"]
    is_cable_1_connected -> is_cable_2_connected [label="Yes"]
    is_cable_2_connected -> connect_cable_2  [label="No"]
    connect_cable_2 -> does_cable_2_light_up [label=""]
    is_cable_1_connected -> connect_cable_1 [label="No"]
    connect_cable_1 -> does_cable_2_light_up  [label=""]
    is_cable_2_connected -> does_base_have_power [label="Yes"]
    does_base_have_power -> replace_one_or_both_cables [label="Yes"]
    does_base_have_power -> supply_power_to_base [label="No"]
    supply_power_to_base -> does_cable_2_light_up [label=""]


    activate_barcoding_in_axware -> select_correct_com_port_in_axware [label="Unable to activate"]
    select_correct_com_port_in_axware -> activate_barcoding_in_axware [label="Retry"]

    activate_barcoding_in_axware -> is_axware_set_to_staging [label="Activated"]


    # Happy Path
    is_handheld_on -> is_scanner_linked
    is_scanner_linked -> link_scanner_with_base [label="No"]
    is_scanner_linked -> does_cable_2_light_up [label="Yes", shape=box, style=filled, fillcolor=yellow ]
    is_barcoding_activated_in_axware -> is_axware_set_to_staging [label="Yes"]
    is_axware_set_to_staging -> does_axware_see_good_data [label="Yes"]
    does_cable_2_light_up -> is_barcoding_activated_in_axware [label="Yes"]

    does_axware_see_good_data -> verify_axware_barcode_settings [label="No (#1)"]
    does_axware_see_good_data -> reset_scanner_and_start_over [label="No (#2)"]
    does_axware_see_good_data -> use_python_to_verify_serial_data [label="No (#3)"]
    does_axware_see_good_data -> success [label="Yes"]

}



