from sim_mobile_robot.teleop import command_for_key


def test_forward_and_reverse_keys():
    assert command_for_key("w") == (0.25, 0.0)
    assert command_for_key("s") == (-0.25, 0.0)


def test_turn_keys():
    assert command_for_key("a") == (0.0, 0.8)
    assert command_for_key("d") == (0.0, -0.8)


def test_space_stops_and_unknown_key_is_ignored():
    assert command_for_key(" ") == (0.0, 0.0)
    assert command_for_key("x") is None


def test_custom_speeds_are_respected():
    assert command_for_key("w", linear_speed=0.4) == (0.4, 0.0)
    assert command_for_key("a", angular_speed=1.2) == (0.0, 1.2)
