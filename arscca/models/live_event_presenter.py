import pdb

class LiveEventPresenter:

    @classmethod
    def diff(cls, previous_drivers, drivers):
        pd_dict = dict([(driver['name'], driver) for driver in previous_drivers])
        d_dict  = dict([(driver['name'], driver) for driver in          drivers])

        pd_names = set(pd_dict.keys())
        d_names  = set( d_dict.keys())

        # "Common" meaning found both in previous_drivers and in drivers
        common_names  = pd_names.intersection(d_names)
        deleted_names = pd_names.difference(d_names)
        added_names   = d_names.difference(pd_names)

        updates = []

        for name in common_names:
            driver = d_dict[name]
            p_driver = pd_dict[name]

            # Note that if a driver is added or deleted,
            # position_overall for many other drivers may
            # change, leading to their being updated
            # IDEALLY: the javascript handles the numbering for position_overall,
            # and then less frequent updates required.
            # BUT: once the event starts, we expect few additions and subtractions
            if driver != p_driver:
                updates.append(driver)

        for name in added_names:
            driver = d_dict[name]
            updates.append(driver)

        output = dict(create=list(added_names),
                      destroy=list(deleted_names),
                      update=updates)

        return output


