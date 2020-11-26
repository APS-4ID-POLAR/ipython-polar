
__all__ = ['local_rd']

from bluesky.plan_stubs import read

def local_rd(obj, *, default_value=0):
    """Reads a single-value non-triggered object
    This is a helper plan to get the scalar value out of a Device
    (such as an EpicsMotor or a single EpicsSignal).
    For devices that have more than one read key the following rules are used:
    - if exactly 1 field is hinted that value is used
    - if no fields are hinted and there is exactly 1 value in the
      reading that value is used
    - if more than one field is hinted an Exception is raised
    - if no fields are hinted and there is more than one key in the reading an
      Exception is raised
    The devices is not triggered and this plan does not create any Events
    Parameters
    ----------
    obj : Device
        The device to be read
    default_value : Any
        The value to return when not running in a "live" RunEngine.
        This come ups when ::
           ret = yield Msg('read', obj)
           assert ret is None
        the plan is passed to `list` or some other iterator that
        repeatedly sends `None` into the plan to advance the
        generator.
    Returns
    -------
    val : Any or None
        The "single" value of the device
    """
    hints = getattr(obj, 'hints', {}).get("fields", [])
    if len(hints) > 1:
        msg = (
            f"Your object {obj} ({obj.name}.{getattr(obj, 'dotted_name', '')}) "
            f"has {len(hints)} items hinted ({hints}).  We do not know how to "
            "pick out a single value.  Please adjust the hinting by setting the "
            "kind of the components of this device or by rd ing one of it's components"
        )
        raise ValueError(msg)
    elif len(hints) == 0:
        hint = None
        if hasattr(obj, "read_attrs"):
            if len(obj.read_attrs) != 1:
                msg = (
                    f"Your object {obj} ({obj.name}.{getattr(obj, 'dotted_name', '')}) "
                    f"and has {len(obj.read_attrs)} read attrs.  We do not know how to "
                    "pick out a single value.  Please adjust the hinting/read_attrs by "
                    "setting the kind of the components of this device or by rd ing one "
                    "of its components"
                )

                raise ValueError(msg)
    # len(hints) == 1
    else:
        (hint,) = hints

    ret = yield from read(obj)

    # list-ify mode
    if ret is None:
        return default_value

    if hint is not None:
        return ret[hint]["value"]

    # handle the no hint 1 field case
    try:
        (data,) = ret.values()
    except ValueError as er:
        msg = (
            f"Your object {obj} ({obj.name}.{getattr(obj, 'dotted_name', '')}) "
            f"and has {len(ret)} read values.  We do not know how to pick out a "
            "single value.  Please adjust the hinting/read_attrs by setting the "
            "kind of the components of this device or by rd ing one of its components"
        )

        raise ValueError(msg) from er
    else:
        return data["value"]
